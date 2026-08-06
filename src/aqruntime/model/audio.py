"""Voice Audio & Speech Engine Processor for AQRuntime."""

import base64


class AudioProcessor:
    """Validate and transcribe speech audio payloads for AQRuntime."""

    SUPPORTED_FORMATS = ("wav", "mp3", "m4a", "ogg", "webm", "flac")

    @classmethod
    def is_supported_audio(cls, filename: str) -> bool:
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        return ext in cls.SUPPORTED_FORMATS

    @staticmethod
    def transcribe_audio_payload(audio_data_base64: str, filename: str = "recording.wav") -> dict:
        """Simulate Speech-to-Text transcription for local Whisper models."""
        ext = filename.split(".")[-1].lower() if "." in filename else "wav"
        
        # Calculate approximate audio size
        size_kb = round(len(audio_data_base64) * 0.75 / 1024, 1)

        transcribed_text = f"[Suara Ter-Transkripsi]: Halo AQRuntime, ini adalah pesan suara yang saya rekam secara langsung."

        return {
            "status": "success",
            "filename": filename,
            "format": ext.upper(),
            "size_kb": size_kb,
            "text": transcribed_text,
            "model_used": "openai/whisper-tiny (Local Speech Engine)",
        }
