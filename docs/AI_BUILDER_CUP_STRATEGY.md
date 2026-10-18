# Google Cloud AI Builder Cup 2026 — AQRuntime WorkDoc Readiness

## Current recommendation

Submit **AQRuntime WorkDoc** under **Future of Work & Enterprise Productivity**, subject to the organizer's final eligibility decision. AQRuntime is the pre-existing runtime foundation; WorkDoc is the new competition-period workflow for asking questions about a work document and reviewing retrieved source passages.

Do not present the whole AQRuntime codebase as if it were created during the hackathon. The organizer clarified that prior work may be referenced, but the evaluated solution must demonstrate substantial new development during the competition timeline.

## Eligibility and AI requirement

- The repository's initial commit is dated August 6, 2026, before the public prototype-building period. That makes the existing codebase's age a material eligibility risk.
- The October 16 commit records substantial source changes during the competition period. Its source diff contains about 1,236 insertions and 58 deletions across runtime, inference, model loading, and API code. Git timestamps are evidence of recorded work, not independent proof of when every change was authored.
- The WorkDoc workflow, evidence retrieval module, citation display, sample document, and Cloud Run packaging were added to this workspace on October 17. They are not yet represented in Git history because the current environment cannot write to `.git`.
- The organizer says the final eligibility decision is made during evaluation. Preserve commit history and describe the pre-existing foundation transparently.
- Google AI requirement has two possible routes in the official event rules: use Gemini/Gemma models or build with an approved agentic platform such as Antigravity. The project owner reports that AQRuntime was built using Google Antigravity. The prototype also uses a quantized Google Gemma model. Do not claim Gemini is integrated; it is not.

## Proposed challenge solution

**Name:** AQRuntime WorkDoc

**Theme:** Future of Work & Enterprise Productivity

**Problem framing:** Small teams need to find specific information in work documents. A general chat box can respond without showing which part of the source supports its answer.

**Prototype response:** WorkDoc retrieves passages from one attached readable text file, asks the selected local model to answer from those excerpts, and displays the excerpts with source IDs and character offsets. If retrieval finds no passage, the workflow says so. If the model does not cite a retrieved source ID, the interface marks its answer as unverified.

**Vision:** Make AI work more inspectable and adaptable for small teams by showing where document answers came from and supporting models that run on available hardware.

## What is implemented

- `/workdoc` serves a separate WorkDoc interface; `/ui` remains the AQRuntime Control Center, and both pages link to each other.
- `/api/workdoc/ask` accepts a model, question, filename, and document text.
- Documents are divided into overlapping passages and ranked with lexical BM25-style scoring.
- The model receives only the top passages with instructions to answer from them and cite markers such as `[S1]`.
- The UI shows the answer, retrieved excerpts, and character offsets.
- Answers without a recognized citation are marked unverified; missing evidence produces a refusal to answer from the document.
- Document request text is not saved to persistent chat history. WorkDoc's warm model cache avoids reloading the model for each follow-up question; the in-memory conversation buffer is cleared after generation.
- A synthetic sample policy is available in `docs/workdoc_demo_sample.md`.

## Honest prototype limits

- One text/code file at a time; supported extensions are `.txt`, `.py`, `.json`, `.md`, `.log`, `.csv`, `.c`, `.cpp`, and `.h`.
- Browser upload is capped at 2 MB; the API caps document text at 100,000 characters and questions at 2,000 characters.
- Retrieval uses lexical terms, not semantic embeddings. A citation marker only confirms that the answer referenced a retrieved passage; it does not guarantee correctness.
- PDF/DOCX/XLSX extraction, multi-document search, OCR, real speech transcription, and real vision inference are outside the WorkDoc workflow.
- Do not claim that document contents remain on the user's device when the Cloud Run version is used. Cloud Run receives the request and performs inference in Google Cloud.

## Cloud Run readiness

- `Dockerfile` builds a Linux CPU image, installs `llama-cpp-python`, and downloads the Gemma 2 2B Q4_K_M model at build time.
- The model file is approximately 1.71 GB. It is excluded from Git and fetched from the public model repository during the image build.
- `.dockerignore` removes local models, Python environments, logs, scratch files, and PoC archives from the build context.
- `.gitignore` now explicitly includes `src/aqruntime/memory` (application source) while retaining the root `memory/` ignore for runtime conversation data. This package was previously hidden by the broad ignore rule and must be present in a deployment source checkout.
- `cloudbuild.yaml` builds and pushes the image to Artifact Registry in `asia-southeast2`; it does not deploy a Cloud Run service.
- The Cloud Run command binds to `0.0.0.0` and reads the platform's `PORT` value.
- Suggested initial service settings: `asia-southeast2`, 4 vCPU, 8 GiB RAM, concurrency 1, maximum instances 1. Keep minimum instances at zero during rehearsals; deciding to keep one instance warm during evaluation may add idle cost.
- Build, Artifact Registry storage, and inference can incur charges. A billing budget alert is a notification, not a hard spending limit.
- Docker and `gcloud` are unavailable in the current development environment. No image build or Cloud Run deployment has been completed.

## Submission status

| Requirement | Status |
| --- | --- |
| One selected theme | Proposed: Future of Work & Enterprise Productivity |
| Substantial new development | WorkDoc source implementation added; must be reviewed and demonstrated |
| Google AI / agentic platform | Antigravity development reported by owner; Gemma GGUF model selected |
| Cloud Run or Firebase live deployment | Not deployed; Cloud Build packaging prepared |
| Public GitHub repository | Existing project repo is public; new changes are local and not pushed yet |
| Pitch deck in prescribed template | Not completed; obtain template from submission dashboard |
| 3–4 minute demo video | Not recorded; organizer confirmed the updated email duration |
| Brief solution description | Can be based on the solution summary above |

## Demo plan

1. State that AQRuntime is the prior runtime foundation and WorkDoc is the new competition-period workflow.
2. Attach the synthetic sample policy.
3. Ask: “What approval is required for a trip estimated to cost USD 1,800?”
4. Show the answer with its source marker and excerpt containing the USD 1,500 threshold.
5. Ask: “What is the reimbursement limit for international roaming?”
6. Show that no matching passage was found and that the assistant does not invent a policy answer.
7. Repeat the same workflow on the live Cloud Run URL after deployment is verified.
