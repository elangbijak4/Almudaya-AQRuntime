# AQRuntime WorkDoc — AI Builder Cup Prototype Notes

## Submission framing

**Challenge theme:** Future of Work & Enterprise Productivity.

**Prototype:** AQRuntime WorkDoc lets a user attach one readable text file, ask a question about it, and inspect the passages retrieved for the answer. The prototype is intended to help small teams locate information in work documents while using an installed local language model.

**Development provenance:** AQRuntime is an existing project that predates the competition. WorkDoc is a new competition-period workflow built on that foundation. This document records the distinction; it does not claim that the AQRuntime codebase itself was created during the hackathon. Eligibility remains subject to the organizer's review.

## New workflow in this prototype

1. The browser reads a supported plain-text file and sends its text with the user's question.
2. The API divides the document into overlapping passages and ranks them using lexical BM25-style relevance scoring.
3. The top passages are sent to the selected AQRuntime model with instructions to answer only from the excerpts and cite source markers such as `[S1]`.
4. The interface displays the answer, retrieved excerpts, and each excerpt's character offsets in the uploaded file.
5. The interface marks answers without a recognized source marker as unverified and reports when no relevant passage was retrieved.

The WorkDoc endpoint does not save document questions or answers to the persistent chat-session store. Request content is handled in memory and the engine's Python conversation buffer is cleared after generation. The loaded model can remain in the runtime's bounded warm cache so follow-up questions do not reload the weights on every request.

## Current prototype limits

- Accepts one readable text/code file at a time. Supported extensions are `.txt`, `.py`, `.json`, `.md`, `.log`, `.csv`, `.c`, `.cpp`, and `.h`.
- Browser upload is limited to 2 MB; the endpoint accepts up to 100,000 characters and a 2,000-character question.
- PDF, DOCX, XLSX, image OCR, audio transcription, multi-document search, and semantic-vector retrieval are not part of this workflow.
- Retrieval is lexical, not embedding-based. A citation marker confirms that the model referenced one of the retrieved passages; it does not prove that the answer is correct. Users should compare the excerpts with the source document.
- Explicit summary requests (English or Indonesian) use a separate path: short documents are passed in full, while longer documents use evenly spaced representative passages and are labeled as partial coverage.
- AQRuntime's existing local model and hardware behavior remain as before. No Cloud Run deployment is claimed by this document.

## Retest results — 18 October 2026

- The repository acceptance suite passed **43/43 tests** using the available Python runtime with the project's installed packages.
- The updated server was started locally on port `8766`. `/health`, `/ui`, `/workdoc`, `/v1/models`, model capabilities, runtimes, Hardware Doctor, pull status, and memory listing returned successfully.
- A live Gemma 2 2B GGUF chat request returned the requested text response. CUDA was reported unavailable; the request ran through the CPU provider.
- WorkDoc answered the synthetic trip-approval question and cited `[S1]`. Its source excerpt showed the department-director threshold. The no-evidence international-roaming question returned `insufficient_evidence` with no citations.
- The screenshot's exact request, “Apakah anda bisa merangkum dokumen ini,” was tested against `AI_BUILD_SPECIFICATION.md.txt`: Gemma produced a summary using all 6 document passages, reported full coverage, and linked the sources. Long-document sampling and Indonesian/English summary detection have regression tests.
- WorkDoc size validation returned HTTP 413 for questions above 2,000 characters, documents above 100,000 characters, and requests above 500 KB. WorkDoc questions did not change the persistent memory list.
- Retesting exposed a retrieval false positive: broad terms such as “reimbursement” and “limit” could match an unrelated meal policy. Retrieval now requires topic-specific term overlap; regression tests cover both the false-positive case and a relevant meal question.
- Hardware Doctor previously displayed missing CPU and model-capacity values. The API now supplies those fields; the updated UI displayed the CPU, 5.2B FP16 limit, and 19.3B GGUF limit.
- Model Hub's cached `facebook/opt-125m` entry was incorrectly shown as a 3B model. Million-parameter IDs and stale generic cache entries now resolve to 0.125B / 0.3 GB estimated RAM.
- The browser rendered WorkDoc, loaded the model selector, and showed its missing-document validation. Document inference was tested through the live HTTP endpoint using the synthetic sample; the browser file-picker upload itself was not automated in this retest.
- Audio transcription is still simulated, not real Whisper inference. Vision inference and Cloud Run deployment were not tested as working features.

The older server already running on port `8765` was left untouched and does not include the new `/workdoc` route. The updated source is running on port `8766` for review. Do not use the older URL to evaluate WorkDoc.

## Cloud Run audit notes

- The application has CLI options to bind a requested host and port. A Cloud Run startup command must bind to `0.0.0.0` and use the `PORT` environment variable.
- `Dockerfile` builds a CPU inference image with `llama-cpp-python` and fetches the Gemma 2 2B Q4_K_M weights from Hugging Face during the image build. The 1.71 GB model is not included in Git; the model card identifies its Gemma license and lists the quantized file size. [Model file and card](https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/blob/main/gemma-2-2b-it-Q4_K_M.gguf)
- `.dockerignore` excludes local model folders, environments, logs, and PoC archives. The `.gitignore` exception keeps the `src/aqruntime/memory` Python package in source control while continuing to exclude runtime session data under the root `memory/` directory.
- `cloudbuild.yaml` builds and pushes the container image to Artifact Registry; it does not deploy a public service. The Cloud Run settings still need to be reviewed in the Console.
- The image is large and its first model load is CPU-bound. Build, image storage, and Cloud Run inference can incur charges. Use a single instance and concurrency of one for the initial demo; keep minimum instances at zero while rehearsing, then decide whether the lower cold-start risk is worth the idle cost during evaluation.
- `gcloud` and Docker are not available in the current development environment. Build and deploy through Google Cloud Build/Cloud Run in the Console or install the CLI and Docker before using command-line deployment.
- Public evaluator access makes the endpoint callable without login. Before enabling it, set the instance/concurrency limits above, create a billing budget alert, and monitor usage. A budget alert notifies you; it is not a hard spending cap.

## Cloud Console deployment outline

1. In Artifact Registry, create a Docker repository named `aqruntime` in `asia-southeast2`.
2. Connect the GitHub repository to a Cloud Build trigger using `cloudbuild.yaml`. Select the submission branch and grant the Cloud Build service account permission to write to the Artifact Registry repository.
3. Run the build. The build downloads the quantized model, so it can take a while and uses Cloud Build resources.
4. In Cloud Run, deploy the resulting `aqruntime-workdoc` image to `asia-southeast2`. Configure 4 vCPU, 8 GiB memory, concurrency 1, maximum instances 1, and public access for evaluator demo use.
5. Open the service URL, check `/health`, select the preloaded Gemma model, and run the document question flow. Keep minimum instances at zero until you have reviewed the expected evaluation-window cost and cold-start tradeoff.

## Demo checklist

- Use a synthetic or non-sensitive sample document.
- Ask a question with names, dates, or terms present in the document.
- Show the answer and the source excerpt with its `[S#]` marker and character offsets.
- Ask one question whose answer is absent and show the insufficient-evidence response.
- State that the runtime foundation predates the event and identify WorkDoc as the new workflow.
- Claim Google Cloud deployment only after the deployed URL has been opened and the same document workflow has been demonstrated there.
