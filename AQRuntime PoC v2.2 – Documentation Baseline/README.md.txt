# README.md

# AQRuntime PoC v2.2 Documentation Baseline

Version: PoC v2.2

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language and vision models locally.
Version PoC v2.2 introduces Multimodal Vision & Image Analysis Engine: Image Upload (`🖼️`), Live Preview Canvas, OpenAI Base64 Multimodal API support, and Vision Catalog Discovery (`aq discover vision`).

## 2. Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aq ui
```

## 3. Supported Commands

```bash
aq ui [--host HOST] [--port PORT] [--no-browser]
aq serve [--host HOST] [--port PORT]
aq doctor
aq discover [query|nvidia|vision]
aq login <token>
aq pull <model> [--token <token>] [--yes]
aq list
aq run <model> [--runtime <provider>] [--memory | --no-memory] [--session <name>] [--system <prompt>]
aq runtime list
aq runtime info <provider>
aq memory <list|clear|export> [name]
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v2.2

- Multimodal Vision & Image Analysis Engine (`VisionProcessor`).
- Image Attachment Upload (`🖼️`) and Live Preview Thumbnail Canvas.
- OpenAI-Compatible Multimodal `image_url` Base64 API Payload.
- Vision Model Discovery Catalog (`aq discover vision`).
- Living Development History file (`docs/Development_History.md`).
