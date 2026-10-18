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

1. Attach one readable text document.
2. Ask a question in natural language.
3. Receive an answer grounded in the most relevant passages.
4. Inspect each retrieved excerpt and its character range in the original text.

If no relevant passage is found, WorkDoc says so. If the model omits a recognized citation, the response is marked unverified.

## Slide 4 — Product demo

Use the synthetic sample document `workdoc_demo_sample.md`.

**Question 1:** “What approval is required for a trip estimated to cost USD 1,800?”

Show the answer citing the passage that says trips above USD 1,500 also need department-director approval, plus the source excerpt and character range.

**Question 2:** “What is the reimbursement limit for international roaming?”

Show that the document has no matching passage and WorkDoc does not invent an answer.

## Slide 5 — How it works

**Browser → WorkDoc API → Passage retrieval → Selected model → Answer + source excerpts**

- The API splits the uploaded text into overlapping passages.
- Lexical BM25-style scoring selects up to four relevant excerpts.
- The selected model is instructed to answer only from those excerpts and cite markers such as `[S1]`.
- The interface displays the answer, citation status, and source offsets.

The prototype uses a quantized Gemma 2 2B GGUF model. Google Antigravity was used as the agentic coding platform during development.

## Slide 6 — Why this approach

- **Inspectable:** users can compare the answer with retrieved source text.
- **Focused:** the prototype addresses one concrete document workflow.
- **Flexible runtime:** AQRuntime can use a model installed on the chosen runtime.
- **Practical scope:** one text file and a small set of evidence passages keep the demo understandable.

## Slide 7 — Intended users and expected value

**Intended users:** small teams that need to find answers in policies, operating guides, or project notes.

**Expected value to validate:** reduce the effort of locating relevant passages and make AI-generated document answers easier to review.

No measured productivity or accuracy claims are made yet. These need to be evaluated with representative users and documents.

## Slide 8 — Technical status and next steps

- AQRuntime is the pre-existing runtime foundation; AQRuntime WorkDoc is the competition-period workflow developed on top of it.
- The local prototype has a dedicated WorkDoc page at `/workdoc`, separate from the existing AQRuntime Control Center at `/ui`; it supports text/code attachments and source excerpts.
- **Cloud Run demo URL (WorkDoc):** `https://aqruntime-workdoc-cvtcvsvijq-et.a.run.app/workdoc`
- **Cloud Run Control Center URL:** `https://aqruntime-workdoc-cvtcvsvijq-et.a.run.app/ui`
- **Status:** Cloud Run container deployed and verified end-to-end with embedded Google Gemma 2 2B IT GGUF (`bartowski/gemma-2-2b-it-GGUF`) and 1-click sample document grounding (`[S1]` source citations).

Do not remove the provenance statement. The organizer's clarification says the new solution must show substantial development during the hackathon and that final eligibility is determined during evaluation.

