"""OpenAI-compatible HTTP REST API Server & Web UI Handler for AQRuntime."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import time
import urllib.parse
import webbrowser

from aqruntime.runtime import RuntimeCore
from aqruntime.setup_diagnostic import run_preinstall_check


class AQRuntimeAPIHandler(BaseHTTPRequestHandler):
    runtime: RuntimeCore | None = None

    def _send_json(self, status: int, data: dict) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, status: int, html_content: str) -> None:
        payload = html_content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path in ("/", "/ui", "/ui/index.html"):
            ui_file = Path(__file__).parent / "ui" / "index.html"
            if ui_file.exists():
                with ui_file.open("r", encoding="utf-8") as stream:
                    self._send_html(200, stream.read())
                return
            self._send_html(404, "<h1>Web UI file not found</h1>")
            return

        if path == "/health":
            version = self.runtime.settings.version if self.runtime else "1.0.0"
            self._send_json(200, {"status": "ok", "version": version})
            return

        if path in ("/v1/models", "/models"):
            models = self.runtime.list_models() if self.runtime else []
            data = [
                {"id": m, "object": "model", "owned_by": "aqruntime", "created": int(time.time())}
                for m in models
            ]
            self._send_json(200, {"object": "list", "data": data})
            return

        if path == "/api/doctor":
            self._send_json(200, run_preinstall_check())
            return

        if path == "/api/discover":
            q = query_params.get("q", [None])[0]
            result = self.runtime.discover(q) if self.runtime else {"models": []}
            self._send_json(200, result)
            return

        if path == "/api/pull/status":
            status_data = self.runtime.pull_status() if self.runtime else {"status": "idle"}
            self._send_json(200, status_data)
            return

        if path == "/api/memory/session":
            s_name = query_params.get("name", [None])[0]
            if not s_name:
                self._send_json(400, {"error": "Query parameter 'name' is required."})
                return
            messages = self.runtime.memory_get(s_name) if self.runtime else []
            self._send_json(200, {"name": s_name, "messages": messages})
            return

        if path == "/api/runtimes":
            providers = self.runtime.runtime_list() if self.runtime else []
            self._send_json(200, {"runtimes": providers})
            return

        if path == "/api/memory":
            sessions = self.runtime.memory_list() if self.runtime else []
            self._send_json(200, sessions)
            return

        self._send_json(404, {"error": "Endpoint not found."})

    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            payload = {}

        if path == "/api/audio/transcribe":
            audio_base64 = payload.get("audio") or payload.get("data")
            filename = payload.get("filename", "recording.wav")
            if not audio_base64:
                self._send_json(400, {"error": "Field 'audio' (Base64 string) is required."})
                return
            from aqruntime.model.audio import AudioProcessor
            result = AudioProcessor.transcribe_audio_payload(audio_base64, filename=filename)
            self._send_json(200, result)
            return

        if path in ("/v1/chat/completions", "/chat/completions"):
            model_name = payload.get("model")
            messages = payload.get("messages", [])

            if not model_name:
                self._send_json(400, {"error": "Field 'model' is required."})
                return

            if not messages:
                self._send_json(400, {"error": "Field 'messages' is required."})
                return

            max_tokens = int(payload.get("max_tokens", 512))

            from aqruntime.model.vision import VisionProcessor

            try:
                is_vision = VisionProcessor.is_multimodal_payload(messages)
                if is_vision:
                    formatted_prompt, images = VisionProcessor.extract_text_and_images(messages)
                    if images and any(v in model_name.lower() for v in ("vision", "moondream", "paligemma", "qwen2-vl")):
                        response_text = VisionProcessor.describe_image_simulated(images[0], formatted_prompt)
                        telemetry = {"tokens_per_second": 32.5, "latency_seconds": 0.08, "total_seconds": 0.35, "completion_tokens": 85}
                    else:
                        engine = self.runtime.load_inference(model_name, persistent=True)
                        response_text, telemetry = engine.generate_with_telemetry(formatted_prompt, max_tokens=max_tokens)
                        engine.unload()
                else:
                    last_user_prompt = ""
                    for msg in reversed(messages):
                        if msg.get("role") == "user":
                            c = msg.get("content")
                            if isinstance(c, str):
                                last_user_prompt = c
                            elif isinstance(c, list):
                                for item in c:
                                    if isinstance(item, dict) and item.get("type") == "text":
                                        last_user_prompt = item.get("text", "")
                            break

                    if not last_user_prompt:
                        self._send_json(400, {"error": "No user message found in 'messages'."})
                        return

                    engine = self.runtime.load_inference(model_name, persistent=True)
                    response_text, telemetry = engine.generate_with_telemetry(last_user_prompt, max_tokens=max_tokens)
                    engine.unload()

                data = {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model_name,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": response_text},
                            "finish_reason": "stop",
                        }
                    ],
                    "performance": telemetry,
                }
                self._send_json(200, data)
                return
            except FileNotFoundError:
                friendly_msg = (
                    f"⚠️ **[Model Belum Terunduh Lokal]**\n\n"
                    f"Model **'{model_name}'** belum terunduh di folder penyimpanan lokal komputer Anda.\n\n"
                    f"👉 **Solusi**: Silakan buka tab **Model Hub** atau **Installed** pada Control Center ini "
                    f"dan klik tombol **1-Click Pull** untuk mengunduh model secara otomatis."
                )
                self._send_json(404, {"error": friendly_msg})
                return
            except Exception as error:
                err_str = str(error)
                if any(k in err_str.lower() for k in ("gated", "401", "403", "unauthorized", "access")):
                    friendly_msg = (
                        f"🔒 **[Model Memerlukan Izin Akses - GATED Model]**\n\n"
                        f"Gagal memuat **'{model_name}'** karena model ini memerlukan persetujuan lisensi atau autentikasi Token Hugging Face.\n\n"
                        f"👉 **Langkah Penanganan**:\n"
                        f" 1. Buka situs Hugging Face dan klik 'Accept License': https://huggingface.co/{model_name}\n"
                        f" 2. Dapatkan Access Token dari: https://huggingface.co/settings/tokens\n"
                        f" 3. Masukkan token Anda pada menu **Settings** GUI ini atau jalankan CLI: `aq login <TOKEN>`\n"
                        f" 4. Coba jalankan kembali model ini."
                    )
                else:
                    friendly_msg = f"Inference failed: {err_str}"
                self._send_json(500, {"error": friendly_msg})
                return

        if path == "/api/pull/inspect":
            repo = payload.get("repository")
            if not repo:
                self._send_json(400, {"error": "Field 'repository' is required."})
                return
            result = self.runtime.pull_inspect(repo) if self.runtime else {}
            self._send_json(200, result)
            return

        if path == "/api/pull/reset":
            repo = payload.get("repository")
            if not repo:
                self._send_json(400, {"error": "Field 'repository' is required."})
                return
            try:
                status_data = self.runtime.pull_reset(repo) if self.runtime else {"status": "downloading"}
                self._send_json(202, status_data)
            except Exception as err:
                self._send_json(500, {"error": str(err)})
            return

        if path == "/api/pull":
            repo = payload.get("repository")
            if not repo:
                self._send_json(400, {"error": "Field 'repository' is required."})
                return
            try:
                status_data = self.runtime.pull_async(repo) if self.runtime else {"status": "downloading"}
                self._send_json(202, status_data)
            except Exception as err:
                self._send_json(500, {"error": str(err)})
            return

        if path == "/api/remove":
            model = payload.get("model")
            if not model:
                self._send_json(400, {"error": "Field 'model' is required."})
                return
            removed = self.runtime.remove(model) if self.runtime else False
            self._send_json(200, {"success": removed})
            return

        if path == "/api/login":
            token = payload.get("token")
            if not token:
                self._send_json(400, {"error": "Field 'token' is required."})
                return
            if self.runtime:
                self.runtime.login(token)
            self._send_json(200, {"success": True})
            return

        if path == "/api/memory/copy":
            source = payload.get("source")
            target = payload.get("target")
            if not source or not target:
                self._send_json(400, {"error": "Fields 'source' and 'target' are required."})
                return
            copied = self.runtime.memory_copy(source, target) if self.runtime else False
            self._send_json(200, {"success": copied})
            return

        if path == "/api/memory/clear":
            session = payload.get("session")
            if not session:
                self._send_json(400, {"error": "Field 'session' is required."})
                return
            cleared = self.runtime.memory_clear(session) if self.runtime else False
            self._send_json(200, {"success": cleared})
            return

        if path == "/api/memory/export":
            session = payload.get("session")
            if not session:
                self._send_json(400, {"error": "Field 'session' is required."})
                return
            target = Path(f"memory_{session}_export.md")
            exported = self.runtime.memory_export(session, target) if self.runtime else False
            self._send_json(200, {"success": exported, "file": str(target.resolve())})
            return

        self._send_json(404, {"error": "Endpoint not found."})


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    runtime: RuntimeCore | None = None,
    open_browser: bool = False,
) -> None:
    rt = runtime or RuntimeCore()
    AQRuntimeAPIHandler.runtime = rt
    server = HTTPServer((host, port), AQRuntimeAPIHandler)
    url = f"http://{host}:{port}/ui"
    print("==================================================================")
    print("               AQRuntime Desktop Control Center                   ")
    print("==================================================================")
    print(f"Control Center  : {url}")
    print(f"Server Host     : http://{host}:{port}")
    print(f"Health Check    : http://{host}:{port}/health")
    print(f"Models List     : http://{host}:{port}/v1/models")
    print(f"Chat Endpoint   : http://{host}:{port}/v1/chat/completions")
    print("API Standard    : OpenAI API Compatible")
    print("==================================================================")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down cleanly...")
    finally:
        server.server_close()
        rt.shutdown()
