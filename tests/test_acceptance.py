"""Acceptance-oriented tests for AQRuntime PoC v2.4 GitHub Release Edition."""

import json
from pathlib import Path
import tempfile
from types import ModuleType
import unittest
from unittest.mock import MagicMock, patch

from aqruntime.catalog import CatalogManager
from aqruntime.config.settings import RuntimeSettings, load_settings
from aqruntime.hardware import HardwareDetector
from aqruntime.memory import MemoryManager
from aqruntime.model.gguf_loader import GGUFModelLoader, SimulatedGGUFModel
from aqruntime.model.power_lock import PowerLockManager
from aqruntime.runtime.inference import InferenceEngine
from aqruntime.runtime.provider_manager import ProviderManager
from aqruntime.runtime import RuntimeCore
from aqruntime.server.api import AQRuntimeAPIHandler
from aqruntime.setup_diagnostic import run_preinstall_check
from aqruntime.storage import StorageManager


class AcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.settings = RuntimeSettings("2.4.0", None, root / "models", root / "logs", None, root)
        self.runtime = RuntimeCore(settings=self.settings)

    def tearDown(self) -> None:
        self.runtime.shutdown()
        self.temp.cleanup()

    def test_tc_001_version(self) -> None:
        self.assertEqual(self.runtime.settings.version, "2.4.0")

    def test_preinstall_diagnostic_check(self) -> None:
        result = run_preinstall_check()
        self.assertIn("status", result)
        self.assertIn("hardware", result)
        self.assertIn("minimum_requirement", result)
        self.assertEqual(result["minimum_requirement"]["lightest_model"], "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

    def test_estimate_download_size(self) -> None:
        size_str = self.runtime.estimate_size("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        self.assertTrue(any(unit in size_str for unit in ("GB", "MB", "Estimated")))

    def test_power_lock_manager_lifecycle(self) -> None:
        self.assertTrue(PowerLockManager.acquire_lock())
        self.assertTrue(PowerLockManager.is_locked())
        self.assertTrue(PowerLockManager.release_lock())
        self.assertFalse(PowerLockManager.is_locked())

    def test_inspect_download_state(self) -> None:
        inspect = self.runtime.pull_inspect("google/gemma-2-2b-it")
        self.assertIn("is_installed", inspect)
        self.assertIn("is_partial", inspect)

    def test_token_login_and_persistence(self) -> None:
        self.runtime.login("hf_test_token_12345")
        reloaded = load_settings(self.settings.root_directory)
        self.assertEqual(reloaded.hf_token, "hf_test_token_12345")

    def test_gated_model_download_guidance(self) -> None:
        with patch("huggingface_hub.snapshot_download") as download:
            download.side_effect = Exception("401 Client Error: Repository Not Found or Gated")
            with self.assertRaises(RuntimeError) as context:
                self.runtime.pull("meta-llama/Llama-3.2-1B-Instruct")
            self.assertIn("GATED model", str(context.exception))
            self.assertIn("aq login", str(context.exception))

    def test_discover_command(self) -> None:
        result = self.runtime.discover()
        self.assertIn("hardware", result)
        self.assertIn("models", result)
        self.assertGreater(result["hardware"]["total_ram_gb"], 0)

    def test_tc_002_to_tc_003_download_and_list_multimodel(self) -> None:
        with patch("huggingface_hub.snapshot_download") as download:
            download.side_effect = lambda **kwargs: Path(kwargs["local_dir"]).mkdir(parents=True, exist_ok=True)
            self.assertEqual(
                self.runtime.pull("google/gemma-2-2b-it"),
                "google-gemma-2-2b-it",
            )
            self.assertEqual(
                self.runtime.pull("google/gemma-2-9b-it"),
                "google-gemma-2-9b-it",
            )
        self.assertEqual(
            self.runtime.list_models(),
            ["google-gemma-2-2b-it", "google-gemma-2-9b-it"],
        )

    def test_tc_008_to_tc_009_remove_and_empty_list(self) -> None:
        self.settings.model_directory.mkdir(parents=True, exist_ok=True)
        (self.settings.model_directory / "google-gemma-2-2b-it").mkdir()
        self.assertTrue(self.runtime.remove("google-gemma-2-2b-it"))
        self.assertEqual(self.runtime.list_models(), [])

    def test_missing_model(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "Model not found"):
            self.runtime.load_inference("non-existent-model")


class GGUFTests(unittest.TestCase):
    def test_gguf_loader_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            self.assertFalse(GGUFModelLoader.is_gguf_dir(path))
            gguf_file = path / "model-Q4_K_M.gguf"
            gguf_file.write_bytes(b"GGUF_TEST_HEADER")
            self.assertTrue(GGUFModelLoader.is_gguf_dir(path))
            self.assertEqual(GGUFModelLoader.find_gguf_file(path), gguf_file)

    def test_gguf_loader_uses_real_local_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir)
            model_file = model_dir / "gemma-Q4_K_M.gguf"
            model_file.write_bytes(b"GGUF_TEST_HEADER")

            llama_cpp = ModuleType("llama_cpp")
            llama_cpp.Llama = MagicMock(side_effect=RuntimeError("llama-cpp unavailable"))
            ctransformers = ModuleType("ctransformers")
            auto_model = MagicMock()
            auto_model.from_pretrained.return_value = MagicMock()
            ctransformers.AutoModelForCausalLM = auto_model

            with patch.dict("sys.modules", {"llama_cpp": llama_cpp, "ctransformers": ctransformers}):
                tokenizer, model = GGUFModelLoader.load_gguf(model_dir, n_ctx=512)

            auto_model.from_pretrained.assert_called_once_with(
                str(model_dir),
                model_file=model_file.name,
                model_type="gemma",
                context_length=512,
                local_files_only=True,
            )
            self.assertNotIsInstance(model, SimulatedGGUFModel)
            self.assertNotIsInstance(tokenizer, SimulatedGGUFModel)

    def test_gguf_hardware_capacity(self) -> None:
        detector = HardwareDetector()
        summary = detector.get_summary()
        self.assertIn("max_safe_gguf_param_b", summary)
        self.assertGreater(summary["max_safe_gguf_param_b"], summary["max_safe_param_b"])

    def test_gguf_inference_generation(self) -> None:
        model = SimulatedGGUFModel(Path("test_model.gguf"))
        engine = InferenceEngine(model, model, persistent=False)
        response = engine.generate("Halo, are you gemma model?")
        self.assertIn("GGUF 4-bit model running locally", response)


class ServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.settings = RuntimeSettings("1.4.0", None, root / "models", root / "logs", None, root)
        self.runtime = RuntimeCore(settings=self.settings)

    def tearDown(self) -> None:
        self.runtime.shutdown()
        self.temp.cleanup()

    def test_server_handler_routes(self) -> None:
        handler = AQRuntimeAPIHandler.__new__(AQRuntimeAPIHandler)
        handler.runtime = self.runtime
        handler.path = "/health"
        handler._send_json = MagicMock()
        handler.do_GET()
        handler._send_json.assert_called_with(200, {"status": "ok", "version": "1.4.0"})

        handler.path = "/v1/models"
        handler._send_json = MagicMock()
        handler.do_GET()
        handler._send_json.assert_called()
        args = handler._send_json.call_args[0]
        self.assertEqual(args[0], 200)
        self.assertEqual(args[1]["object"], "list")

        handler.path = "/api/doctor"
        handler._send_json = MagicMock()
        handler.do_GET()
        handler._send_json.assert_called()
        self.assertEqual(handler._send_json.call_args[0][0], 200)
        self.assertIn("cpu", handler._send_json.call_args[0][1]["hardware"])
        self.assertIn("max_safe_param_b", handler._send_json.call_args[0][1]["hardware"])
        self.assertIn("max_safe_gguf_param_b", handler._send_json.call_args[0][1]["hardware"])

        handler.path = "/api/discover"
        handler._send_json = MagicMock()
        handler.do_GET()
        handler._send_json.assert_called()
        self.assertEqual(handler._send_json.call_args[0][0], 200)

        handler.path = "/api/pull/status"
        handler._send_json = MagicMock()
        handler.do_GET()
        handler._send_json.assert_called()
        self.assertEqual(handler._send_json.call_args[0][0], 200)

        handler.path = "/ui"
        handler._send_html = MagicMock()
        handler.do_GET()
        handler._send_html.assert_called()
        self.assertEqual(handler._send_html.call_args[0][0], 200)

        handler.path = "/workdoc"
        handler._send_html = MagicMock()
        handler.do_GET()
        handler._send_html.assert_called_once()
        self.assertEqual(handler._send_html.call_args[0][0], 200)
        self.assertIn("AQRuntime WorkDoc", handler._send_html.call_args[0][1])


class MemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.mem = MemoryManager(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_session_save_and_load(self) -> None:
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Hello, I am Budi."},
            {"role": "assistant", "content": "Nice to meet you, Budi!"},
        ]
        self.mem.save_session("test_session", messages)
        loaded = self.mem.load_session("test_session")
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["content"], "Hello, I am Budi.")

    def test_memory_clear(self) -> None:
        self.mem.save_session("to_delete", [{"role": "user", "content": "hi"}])
        self.assertTrue(self.mem.clear_session("to_delete"))
        self.assertEqual(self.mem.load_session("to_delete"), [])

    def test_memory_copy_and_get(self) -> None:
        messages = [{"role": "user", "content": "Hello Gemma"}]
        self.mem.save_session("gemma_session", messages)
        self.assertTrue(self.mem.copy_session("gemma_session", "tinyllama_session"))
        copied_messages = self.mem.get_session_messages("tinyllama_session")
        self.assertEqual(len(copied_messages), 1)
        self.assertEqual(copied_messages[0]["content"], "Hello Gemma")

    def test_sliding_window(self) -> None:
        messages = [{"role": "system", "content": "System"}]
        for i in range(20):
            messages.append({"role": "user", "content": f"msg {i}"})
        windowed = MemoryManager.apply_short_term_window(messages, max_history_turns=6)
        self.assertEqual(len(windowed), 7)
        self.assertEqual(windowed[0]["role"], "system")
        self.assertEqual(windowed[-1]["content"], "msg 19")


class HardwareAndCatalogTests(unittest.TestCase):
    def test_catalog_estimates_million_parameter_models(self) -> None:
        self.assertEqual(CatalogManager._estimate_param_size("facebook/opt-125m"), 0.125)
        self.assertEqual(CatalogManager._estimate_param_size("Qwen/Qwen3-0.6B"), 0.6)

    def test_catalog_refreshes_stale_cached_million_estimate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cache = root / "config" / "catalog_cache.json"
            cache.parent.mkdir(parents=True)
            cache.write_text(
                json.dumps([{
                    "repo_id": "facebook/opt-125m",
                    "name": "opt-125m",
                    "param_size_b": 3.0,
                    "est_ram_gb": 6.6,
                    "is_gated": False,
                    "description": "Hugging Face model (facebook/opt-125m).",
                }]),
                encoding="utf-8",
            )
            models = CatalogManager(root).load_cached_catalog()
            model = next(item for item in models if item["repo_id"] == "facebook/opt-125m")
            self.assertEqual(model["param_size_b"], 0.125)
            self.assertEqual(model["est_ram_gb"], 0.3)

    def test_hardware_detector(self) -> None:
        detector = HardwareDetector()
        summary = detector.get_summary()
        self.assertGreater(summary["total_ram_gb"], 0)
        self.assertGreater(summary["max_safe_param_b"], 0)

    def test_catalog_offline_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog = CatalogManager(root)
            discovered = catalog.discover_models()
            self.assertIn("hardware", discovered)
            self.assertIn("models", discovered)

    def test_nvidia_catalog_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog = CatalogManager(root)
            discovered = catalog.discover_models("nvidia")
            self.assertIn("models", discovered)
            nvidia_models = [m for m in discovered["models"] if "nvidia" in m["repo_id"].lower()]
            self.assertGreater(len(nvidia_models), 0)

    def test_vision_catalog_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog = CatalogManager(root)
            discovered = catalog.discover_models("vision")
            self.assertIn("models", discovered)
            vision_models = [m for m in discovered["models"] if m.get("format") == "vision" or "moondream" in m["repo_id"].lower()]
            self.assertGreater(len(vision_models), 0)

    def test_audio_catalog_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog = CatalogManager(root)
            discovered = catalog.discover_models("audio")
            self.assertIn("models", discovered)
            audio_models = [m for m in discovered["models"] if m.get("format") == "audio" or "whisper" in m["repo_id"].lower()]
            self.assertGreater(len(audio_models), 0)

    def test_audio_processor(self) -> None:
        from aqruntime.model.audio import AudioProcessor
        self.assertTrue(AudioProcessor.is_supported_audio("voice.wav"))
        self.assertTrue(AudioProcessor.is_supported_audio("recording.mp3"))
        result = AudioProcessor.transcribe_audio_payload("dummybase64data", "sample.wav")
        self.assertEqual(result["status"], "simulated")
        self.assertIn("text", result)
        self.assertIn("not a real Whisper", result["note"])

    def test_max_tokens_configuration(self) -> None:
        model = SimulatedGGUFModel(Path("models/bartowski-gemma-2-2b-it-gguf"))
        engine = InferenceEngine(model, model)
        response = engine.generate("Tell me a story", max_tokens=2048)
        self.assertIn("GGUF 4-bit model", response)


class StorageTests(unittest.TestCase):
    def test_sanitized_full_repository_name(self) -> None:
        self.assertEqual(
            StorageManager.model_name("TinyLlama/TinyLlama-1.1B-Chat-v1.0"),
            "tinyllama-tinyllama-1-1b-chat-v1-0",
        )
        self.assertEqual(
            StorageManager.model_name("google/gemma-2-2b-it"),
            "google-gemma-2-2b-it",
        )

    def test_alias_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir)
            (model_dir / "google-gemma-2-2b-it").mkdir(parents=True, exist_ok=True)
            storage = StorageManager(model_dir)
            self.assertEqual(
                storage.path_for("gemma-2-2b"),
                model_dir / "google-gemma-2-2b-it",
            )


class ChatTemplateTests(unittest.TestCase):
    def test_fallback_contains_clear_chat_roles(self) -> None:
        class Tokenizer:
            chat_template = None

        formatted = InferenceEngine(Tokenizer(), object()).format_prompt("Hello")
        self.assertEqual(
            formatted,
            "System: You are AQRuntime Assistant. Be helpful, truthful, concise, and conversational. "
            "Answer directly in the user's language.\n\n"
            "User: Hello\n\nAssistant:",
        )

    def test_custom_system_prompt_override(self) -> None:
        class Tokenizer:
            chat_template = None

        engine = InferenceEngine(Tokenizer(), object(), system_prompt="You are a pirate.")
        formatted = engine.format_prompt("Ahoy")
        self.assertIn("System: You are a pirate.", formatted)

    def test_native_template_is_used(self) -> None:
        class Tokenizer:
            chat_template = "native"

            def apply_chat_template(self, messages, tokenize, add_generation_prompt):
                self.messages = messages
                self.options = (tokenize, add_generation_prompt)
                return "native prompt"

        tokenizer = Tokenizer()
        self.assertEqual(InferenceEngine(tokenizer, object()).format_prompt("Hello"), "native prompt")
        self.assertEqual(tokenizer.messages[0]["role"], "system")
        self.assertEqual(tokenizer.messages[0]["content"], InferenceEngine.system_prompt)
        self.assertEqual(tokenizer.messages[-1], {"role": "user", "content": "Hello"})
        self.assertEqual(tokenizer.options, (False, True))


class WorkDocTests(unittest.TestCase):
    def test_summary_request_detects_indonesian_and_english(self) -> None:
        from aqruntime.workdoc import is_summary_request

        self.assertTrue(is_summary_request("Apakah anda bisa merangkum dokumen ini"))
        self.assertTrue(is_summary_request("Summarize this document"))
        self.assertFalse(is_summary_request("What is the project purpose?"))

    def test_summary_retrieval_covers_short_build_specification(self) -> None:
        from pathlib import Path
        from aqruntime.workdoc import retrieve_summary_evidence

        document = (Path(__file__).resolve().parents[1] / "AI_BUILD_SPECIFICATION.md.txt").read_text(encoding="utf-8")
        sources, total = retrieve_summary_evidence(document, "AI_BUILD_SPECIFICATION.md.txt")
        self.assertEqual(total, len(sources))
        self.assertEqual(sources[0]["start_char"], 0)
        self.assertEqual(sources[-1]["end_char"], len(document.rstrip()))

    def test_long_summary_retrieval_is_evenly_sampled(self) -> None:
        from aqruntime.workdoc import MAX_SUMMARY_CHUNKS, retrieve_summary_evidence

        document = ("This is a paragraph about the project.\n" * 500)
        sources, total = retrieve_summary_evidence(document, "long.txt")
        self.assertGreater(total, MAX_SUMMARY_CHUNKS)
        self.assertLessEqual(len(sources), MAX_SUMMARY_CHUNKS)
        self.assertEqual(sources[0]["start_char"], 0)
        self.assertGreater(sources[-1]["end_char"], len(document) - 1000)

    def test_retrieval_rejects_shared_generic_terms_without_topic_match(self) -> None:
        from aqruntime.workdoc import retrieve_evidence

        document = "Meal reimbursement is capped at USD 60 per person per day."
        self.assertEqual(
            retrieve_evidence(document, "What is the international roaming reimbursement limit?", "sample.txt"),
            [],
        )

    def test_retrieval_keeps_matching_specific_topic(self) -> None:
        from aqruntime.workdoc import retrieve_evidence

        document = "Meal reimbursement is capped at USD 60 per person per day."
        sources = retrieve_evidence(document, "What is the meal reimbursement limit?", "sample.txt")
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["source_id"], "S1")

    def test_workdoc_sample_loader(self) -> None:
        from aqruntime.workdoc import load_sample_document

        sample = load_sample_document()
        self.assertEqual(sample["filename"], "workdoc_demo_sample.md")
        self.assertIn("Northstar Studio", sample["document_text"])
        self.assertGreater(len(sample["sample_questions"]), 0)


class ProviderManagerTests(unittest.TestCase):
    def test_provider_manager_list(self) -> None:
        mgr = ProviderManager()
        providers = mgr.list_providers()
        self.assertGreater(len(providers), 0)
        names = [p["name"] for p in providers]
        self.assertIn("cpu", names)
        self.assertIn("intel_openvino", names)
        self.assertIn("directml", names)

    def test_provider_manager_info(self) -> None:
        mgr = ProviderManager()
        info = mgr.get_provider_info("intel-npu")
        self.assertEqual(info["display_name"], "Intel NPU")
        self.assertIn("supported_tasks", info)

    def test_provider_manager_formatted_output(self) -> None:
        mgr = ProviderManager()
        fmt_list = mgr.format_runtime_list()
        self.assertIn("AQRuntime Available Runtimes", fmt_list)
        self.assertIn("✓ CPU", fmt_list)
        fmt_info = mgr.format_runtime_info("intel-npu")
        self.assertIn("AQRuntime Provider Info", fmt_info)

    def test_performance_telemetry(self) -> None:
        class DummyModel:
            is_gguf = True
            def generate_text(self, prompt):
                return "This is a test response generated by the simulated model."

        engine = InferenceEngine(object(), DummyModel(), persistent=False)
        response, telemetry = engine.generate_with_telemetry("Hello")
        self.assertIn("tokens_per_second", telemetry)
        self.assertIn("latency_seconds", telemetry)
        self.assertIn("total_seconds", telemetry)
        self.assertGreater(telemetry["tokens_per_second"], 0)

    def test_single_turn_requests_preserve_persistent_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = MemoryManager(Path(tmpdir))
            model = SimulatedGGUFModel(Path("test_model.gguf"))
            engine1 = InferenceEngine(model, model, memory_manager=mem, session_name="chat_s", persistent=True)
            engine1.generate_messages([{"role": "user", "content": "My name is Aslan."}])

            engine2 = InferenceEngine(model, model, memory_manager=mem, session_name="chat_s", persistent=True)
            engine2.generate_messages([{"role": "user", "content": "What is my name?"}])

            saved = mem.load_session("chat_s")
            self.assertEqual(len(saved), 4)
            self.assertEqual(saved[0]["content"], "My name is Aslan.")
            self.assertEqual(saved[2]["content"], "What is my name?")

    def test_warm_cache_shared_between_chat_and_workdoc(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = RuntimeSettings("2.4.0", None, root / "models", root / "logs", None, root, max_cached_models=1)
            (root / "models" / "test-model").mkdir(parents=True)
            rt = RuntimeCore(settings=settings)
            try:
                fake_tok = SimulatedGGUFModel(Path("test.gguf"))
                fake_mod = SimulatedGGUFModel(Path("test.gguf"))
                with patch.object(rt.providers.providers["cpu"], "load_model", return_value=(fake_tok, fake_mod)) as mock_load:
                    eng_chat = rt.load_inference("test-model", persistent=True, provider="cpu")
                    eng_workdoc = rt.load_inference("test-model", persistent=False, provider="cpu", cache_model=True)
                    self.assertEqual(mock_load.call_count, 1)
                    self.assertIs(eng_chat.model, eng_workdoc.model)
                    self.assertTrue(eng_chat.persistent)
                    self.assertFalse(eng_workdoc.persistent)
            finally:
                rt.shutdown()

    def test_gemini_cloud_model_integration_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = RuntimeSettings("2.4.0", None, root / "models", root / "logs", None, root)
            rt = RuntimeCore(settings=settings)
            try:
                with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key_abc"}):
                    chat_models = rt.list_chat_models()
                    self.assertIn("gemini-2.5-flash", chat_models)
                    with patch("aqruntime.providers.gemini.chat", return_value=("Grounded answer [S1]", {"tokens_per_second": 40.0})):
                        engine = rt.load_inference("gemini-2.5-flash", persistent=False)
                        ans = engine.generate_messages([{"role": "user", "content": "Test question"}])
                        self.assertEqual(ans, "Grounded answer [S1]")
            finally:
                rt.shutdown()


if __name__ == "__main__":
    unittest.main()

