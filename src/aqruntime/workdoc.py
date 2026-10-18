"""Evidence retrieval helpers for AQRuntime's work-document assistant."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re


MAX_DOCUMENT_CHARS = 100_000
MAX_QUESTION_CHARS = 2_000
CHUNK_CHARS = 900
CHUNK_OVERLAP = 120
MAX_EVIDENCE_CHUNKS = 4
MAX_SUMMARY_CHUNKS = 8

_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)
_STOP_WORDS = {
    "a", "about", "an", "and", "are", "as", "at", "be", "been", "by", "can", "for", "from", "how",
    "i", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "what", "when",
    "where", "which", "who", "why", "with", "you", "yang", "dan", "di", "dari", "ini", "itu", "ke",
    "pada", "untuk", "apa", "bagaimana", "kapan", "siapa", "mengapa", "dengan", "adalah", "atau",
}
_GENERIC_DOCUMENT_TERMS = {
    "amount", "approval", "approve", "approved", "cost", "document", "expense", "limit", "policy",
    "reimburse", "reimbursement", "required", "requirement", "rule", "rules", "total",
}
_SUMMARY_INTENT_RE = re.compile(
    r"\b(?:summar(?:y|ize|ise|ization)|overview|merangkum|rangkuman|ringkasan|ringkas)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EvidenceChunk:
    source_id: str
    start_char: int
    end_char: int
    text: str
    score: float

    def to_dict(self, filename: str) -> dict:
        return {
            "source_id": self.source_id,
            "filename": filename,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "excerpt": self.text,
        }


def _tokens(text: str) -> list[str]:
    return [token.casefold() for token in _TOKEN_RE.findall(text) if len(token) > 1 and token.casefold() not in _STOP_WORDS]


def _singular(term: str) -> str:
    if term.endswith("ies") and len(term) > 4:
        return term[:-3] + "y"
    if term.endswith("s") and not term.endswith("ss") and len(term) > 4:
        return term[:-1]
    return term


def _split_chunks(text: str) -> list[tuple[int, int, str]]:
    chunks: list[tuple[int, int, str]] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + CHUNK_CHARS, text_length)
        if end < text_length:
            boundary = max(text.rfind("\n", start + CHUNK_CHARS // 2, end), text.rfind(" ", start + CHUNK_CHARS // 2, end))
            if boundary > start:
                end = boundary
        excerpt = text[start:end].strip()
        if excerpt:
            left_trim = len(text[start:end]) - len(text[start:end].lstrip())
            right_trim = len(text[start:end].rstrip())
            chunks.append((start + left_trim, start + right_trim, excerpt))
        if end >= text_length:
            break
        start = max(start + 1, end - CHUNK_OVERLAP)
    return chunks


def is_summary_request(question: str) -> bool:
    """Detect explicit document-summary requests in English or Indonesian."""
    return bool(_SUMMARY_INTENT_RE.search(question))


def retrieve_summary_evidence(document: str, filename: str, limit: int = MAX_SUMMARY_CHUNKS) -> tuple[list[dict], int]:
    """Select the whole short document or evenly spaced excerpts for long ones."""
    chunks = _split_chunks(document)
    if not chunks:
        return [], 0
    count = max(1, min(limit, MAX_SUMMARY_CHUNKS))
    if len(chunks) <= count:
        selected = list(enumerate(chunks))
    else:
        indices = sorted({round(position * (len(chunks) - 1) / (count - 1)) for position in range(count)}) if count > 1 else [0]
        selected = [(index, chunks[index]) for index in indices]
    sources = [
        EvidenceChunk(f"S{rank}", start, end, excerpt, 1.0).to_dict(filename)
        for rank, (_, (start, end, excerpt)) in enumerate(selected, start=1)
    ]
    return sources, len(chunks)


def retrieve_evidence(document: str, question: str, filename: str, limit: int = MAX_EVIDENCE_CHUNKS) -> list[dict]:
    """Return the highest-overlap passages with stable source offsets."""
    chunks = _split_chunks(document)
    query_terms = set(_tokens(question))
    if not chunks or not query_terms:
        return []

    # Broad policy words often overlap across unrelated topics. Require the
    # retrieved text to match most topic-specific terms before treating it as
    # evidence (for example, a meal cap must not answer a roaming question).
    anchor_terms = {_singular(term) for term in query_terms - _GENERIC_DOCUMENT_TERMS if not term.isdigit()}

    tokenized = [_tokens(chunk[2]) for chunk in chunks]
    doc_freq: dict[str, int] = {}
    for terms in tokenized:
        for term in set(terms):
            doc_freq[term] = doc_freq.get(term, 0) + 1

    scored: list[tuple[float, int]] = []
    average_length = max(1.0, sum(map(len, tokenized)) / len(tokenized))
    for index, terms in enumerate(tokenized):
        normalized_terms = {_singular(term) for term in terms}
        if anchor_terms and len(anchor_terms & normalized_terms) / len(anchor_terms) < 0.6:
            continue
        frequencies: dict[str, int] = {}
        for term in terms:
            frequencies[term] = frequencies.get(term, 0) + 1
        score = 0.0
        for term in query_terms:
            frequency = frequencies.get(term, 0)
            if not frequency:
                continue
            inverse_document_frequency = math.log(1 + (len(chunks) - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            denominator = frequency + 1.2 * (0.25 + 0.75 * len(terms) / average_length)
            score += inverse_document_frequency * frequency * 2.2 / denominator
        if score > 0:
            scored.append((score, index))

    selected = sorted(scored, reverse=True)[: max(1, min(limit, MAX_EVIDENCE_CHUNKS))]
    selected.sort(key=lambda item: item[1])
    results = []
    for rank, (score, index) in enumerate(selected, start=1):
        start, end, excerpt = chunks[index]
        results.append(EvidenceChunk(f"S{rank}", start, end, excerpt, score).to_dict(filename))
    return results


def cited_source_ids(answer: str, sources: list[dict]) -> list[str]:
    """Keep only citation IDs actually present in the retrieved evidence."""
    available = {source["source_id"] for source in sources}
    mentioned = re.findall(r"\[(S\d+)\]", answer, flags=re.IGNORECASE)
    return list(dict.fromkeys(source_id.upper() for source_id in mentioned if source_id.upper() in available))


SAMPLE_WORKDOC_FILENAME = "workdoc_demo_sample.md"
SAMPLE_WORKDOC_TEXT = """# Northstar Studio — Travel and Expense Policy

This synthetic sample is for demonstrating AQRuntime WorkDoc. It contains no real company or employee information.

## Approval

Employees must receive written manager approval before booking any business trip. Requests should include the destination, business purpose, travel dates, and estimated total cost. Trips expected to cost more than USD 1,500 also require approval from the department director.

## Booking

Travelers should book economy-class flights at least 14 days before departure when practical. A different cabin class requires an accessibility accommodation or written approval from the department director. Hotels should be within the organization's standard rate for the destination; if no rate is listed, employees should choose a safe, reasonably priced option near the work location.

## Reimbursement

Employees must submit an expense report within 10 calendar days after returning. Receipts are required for any single expense of USD 25 or more. Meal reimbursement is capped at USD 60 per person per day, including tax and tip. Alcohol is not reimbursable.

## Changes and cancellations

If a business need changes, travelers should notify their manager and cancel or change reservations as soon as possible. Any cancellation fee must include a short explanation in the expense report. Personal travel extensions are allowed only when they do not increase the organization's travel cost and are approved in writing before booking.
"""


def load_sample_document() -> dict:
    """Return the synthetic sample document for 1-click evaluator demos."""
    from pathlib import Path

    sample_path = Path(__file__).resolve().parents[2] / "docs" / SAMPLE_WORKDOC_FILENAME
    text = SAMPLE_WORKDOC_TEXT
    if sample_path.is_file():
        try:
            text = sample_path.read_text(encoding="utf-8")
        except Exception:
            text = SAMPLE_WORKDOC_TEXT
    return {
        "filename": SAMPLE_WORKDOC_FILENAME,
        "document_text": text,
        "sample_questions": [
            "What approval is required for a trip estimated to cost USD 1,800?",
            "What is the meal reimbursement limit per day?",
            "What is the reimbursement limit for international roaming?",
            "Summarize this document.",
        ],
    }

