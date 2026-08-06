# AQRuntime

Version: PoC v0.1

---

## Overview

AQRuntime is a lightweight AI Runtime designed to download, manage, load, and execute AI models through a simple command-line interface.

The purpose of AQRuntime PoC v0.1 is to demonstrate the complete execution lifecycle of an AI model, from downloading a model repository to performing interactive inference.

This version intentionally focuses on a minimal implementation and excludes advanced runtime features.

---

## Objectives

AQRuntime PoC v0.1 shall be able to:

- Download AI models from an online repository.
- Store downloaded models locally.
- List installed models.
- Load a selected model.
- Execute inference interactively.
- Remove installed models.

---

## Scope

Included:

- Command Line Interface (CLI)
- Local Model Store
- Model Download
- Model Loading
- Interactive Prompt
- Text Generation

Excluded:

- Agent Runtime
- Multi-Agent System
- Plugin System
- Hardware Abstraction Layer
- NPU Support
- GPU Optimization
- Multi Backend Runtime
- Workflow Engine
- Memory System
- Distributed Runtime

---

## Command Line Interface

AQRuntime provides the following commands.

```bash
aq pull <model>

aq list

aq run <model>

aq remove <model>

aq version
```

---

## Example

Download a model.

```bash
aq pull TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

List installed models.

```bash
aq list
```

Run the model.

```bash
aq run tinyllama
```

Interactive prompt.

```
AQRuntime>

Hello

Model>
Hello! How can I help you today?

AQRuntime>
```

Exit.

```
exit
```

---

## Project Structure

```
AQRuntime/

README.md
MANIFEST.md
REQUIREMENTS.md
DESIGN.md
DATABASE.md
AI_SDK.md
IMPLEMENTATION.md
TESTING.md
```

---

## Proof of Concept

AQRuntime PoC v0.1 is considered complete when:

- Model download succeeds.
- Model storage succeeds.
- Model loading succeeds.
- Interactive inference succeeds.
- Model removal succeeds.
- All acceptance tests pass.

---

## License

Prototype / Research Project.