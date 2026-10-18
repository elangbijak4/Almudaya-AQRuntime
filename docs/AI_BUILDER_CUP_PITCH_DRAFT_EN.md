# AQRuntime WorkDoc — Pitch Deck Content Draft

**Use:** Transfer this content into the prescribed AI Builder Cup deck template. Replace every deployment placeholder only after the live Cloud Run workflow has been verified. No impact metrics are claimed in this draft.

## Slide 1 — Title

### AQRuntime WorkDoc
**Evidence-linked answers for everyday work documents**

A document Q&A workflow that retrieves relevant passages, answers with a selected language model, and shows users where the answer came from.

Challenge theme: **Future of Work & Enterprise Productivity**

## Slide 2 — The problem

Teams often need a specific answer from a policy, guide, or project document. Manual searching takes time, while a chat answer without a visible source can be difficult to verify.

**Design goal:** Make document answers easier to inspect by showing the evidence passages alongside the response.

## Slide 3 — The solution

AQRuntime WorkDoc lets a user:

1. Attach a work document (`.pdf`, `.docx`, `.rtf`, `.txt`, `.md`, `.csv`, `.json`, or source code) or load the built-in 1-click sample policy.
2. Ask specific questions, request summaries, or hold an interactive multi-turn discussion in English or Bahasa Indonesia.
3. Receive answers grounded in retrieved passages with exact `[S1]` source citations.
4. Inspect each retrieved excerpt and its character range in the original text.

If a specific factual topic is not in the document, WorkDoc explicitly states that the document does not mention it rather than guessing.

## Slide 4 — Product demo

Use the live Cloud Run URL (`https://aqruntime-workdoc-cvtcvsvijq-et.a.run.app/workdoc`) and click **“📋 Load sample travel & expense policy (1-click demo)”** (or upload a `.pdf` / `.docx` file).

**Step 1 (Grounded Q&A):** Click *“Approval for USD 1,800 trip?”* → Shows the grounded answer citing `[S1]` (trips above USD 1,500 require department-director approval) along with the exact source excerpt and character offsets.

**Step 2 (Multi-turn & Bilingual Discussion):** Ask a follow-up question or click *“Diskusikan dalam Bahasa Indonesia”* → Shows interactive multi-turn document discussion with context retention.

**Step 3 (Anti-Hallucination Guardrail):** Click *“International roaming limit?”* → Shows that WorkDoc refuses to invent a number when the topic is absent from the document.

## Slide 5 — How it works

**Browser → WorkDoc Extract & Ask API → Bilingual & Contextual Passage Retrieval → Google Gemma 2 2B / Gemini → Answer + Source Excerpts**

- Automatic text extractor parses `.pdf`, `.docx`, `.rtf`, and text/code files into clean UTF-8 text.
- Overlapping passage chunking + lexical BM25 scoring with bilingual synonym expansion and multi-turn conversation history selects the most relevant excerpts.
- The selected Google AI model (**Google Gemma 2 2B IT GGUF** embedded in Cloud Run, with optional **Google Gemini** hybrid support) answers from those excerpts and cites markers such as `[S1]`.
- Built with **Google Antigravity** as the agentic coding platform and deployed on **Google Cloud Run**.

## Slide 6 — Why this approach

- **Inspectable:** users can compare every answer with retrieved source text and character offsets.
- **Interactive:** supports both strict factual Q&A and multi-turn document discussion across English and Bahasa Indonesia.
- **Dual-Mode Runtime (Cloud + Local):** runs self-contained on **Google Cloud Run** for instant browser access and 100% offline on local PCs (CPU/GPU/NPU).
- **Broad Document Support:** handles everyday `.pdf`, `.docx`, `.txt`, `.md`, `.csv`, and code files up to 5 MB.

## Slide 7 — Intended users and expected value

**Intended users:** teams, researchers, and enterprises that need to review, discuss, and verify answers from policies, operating guides, or technical documents.

**Expected value to validate:** reduce the effort of locating relevant passages and make AI-generated document answers easier to audit and verify.

No measured productivity or accuracy claims are made yet. These need to be evaluated with representative users and documents.

## Slide 8 — Technical status and next steps

- AQRuntime is the pre-existing runtime foundation; **AQRuntime WorkDoc** is the competition-period interactive document workflow developed on top of it.
- **Live Cloud Run WorkDoc URL:** `https://aqruntime-workdoc-cvtcvsvijq-et.a.run.app/workdoc`
- **Live Cloud Run Control Center URL:** `https://aqruntime-workdoc-cvtcvsvijq-et.a.run.app/ui`
- **Public GitHub Repository:** `https://github.com/elangbijak4/Almudaya-AQRuntime`
- **Status:** Deployed and verified end-to-end on Google Cloud Run (`asia-southeast2`) with embedded Google Gemma 2 2B IT GGUF, multi-turn discussion, PDF/DOCX extraction, and 49/49 passing acceptance tests.

Do not remove the provenance statement. The organizer's clarification says the new solution must show substantial development during the hackathon and that final eligibility is determined during evaluation.

