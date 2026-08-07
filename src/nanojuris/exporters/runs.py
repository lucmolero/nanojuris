"""Export helpers for saved research runs."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

RUN_EXPORT_FORMATS = {"json", "jsonl", "csv", "markdown"}


def research_run_to_export(
    run: dict[str, Any],
    records: list[dict[str, Any]],
    output_format: str,
) -> str:
    """Serialize one saved research run and its records."""

    normalized = output_format.strip().lower()
    if normalized == "json":
        return json.dumps(
            {"run": run, "records": records},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    if normalized == "jsonl":
        return "\n".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records
        )
    if normalized == "csv":
        return _records_to_csv(records)
    if normalized == "markdown":
        return _records_to_markdown(run, records)
    raise ValueError("Unsupported run export format. Use: json, jsonl, csv or markdown.")


def _records_to_csv(records: list[dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=_CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for record in records:
        writer.writerow(_record_row(record))
    return output.getvalue()


def _records_to_markdown(run: dict[str, Any], records: list[dict[str, Any]]) -> str:
    title = run.get("label") or run.get("text") or run.get("id")
    lines = [f"# Pesquisa NanoJuris: {title}", ""]
    lines.append(f"- Run ID: `{run.get('id')}`")
    lines.append(f"- Fonte: `{run.get('source')}`")
    lines.append(f"- Texto: {run.get('text') or ''}")
    lines.append(f"- Criada em: `{run.get('created_at')}`")
    lines.append(f"- Registros: {len(records)}")
    lines.append("")
    for index, record in enumerate(records, start=1):
        lines.extend(_record_markdown(index, record))
        lines.append("")
    return "\n".join(lines).strip()


def _record_markdown(index: int, record: dict[str, Any]) -> list[str]:
    kind = _record_kind(record)
    title_parts = [f"## {index}. {kind}"]
    if record.get("court"):
        title_parts.append(str(record["court"]))
    if record.get("case_number"):
        title_parts.append(str(record["case_number"]))
    if record.get("precedent_type"):
        title_parts.append(str(record["precedent_type"]))
    lines = [" - ".join(title_parts), ""]
    for label, key in _MARKDOWN_FIELDS:
        if record.get(key):
            lines.append(f"- {label}: {record[key]}")
    source_trace = record.get("source_trace") or {}
    if source_trace.get("source_url"):
        lines.append(f"- URL da fonte: {source_trace['source_url']}")
    return lines


def _record_row(record: dict[str, Any]) -> dict[str, Any]:
    source_trace = record.get("source_trace") or {}
    extraction_trace = record.get("extraction_trace") or {}
    return {
        "record_kind": _record_kind(record),
        "id": record.get("id"),
        "source": record.get("source"),
        "court": record.get("court"),
        "case_number": record.get("case_number"),
        "registry_number": record.get("registry_number"),
        "decision_type": record.get("decision_type"),
        "precedent_type": record.get("precedent_type"),
        "number": record.get("number"),
        "case_class": record.get("case_class"),
        "subject": record.get("subject"),
        "rapporteur": record.get("rapporteur"),
        "judging_body": record.get("judging_body"),
        "origin_county": record.get("origin_county"),
        "judgment_date": record.get("judgment_date"),
        "publication_date": record.get("publication_date"),
        "status": record.get("status"),
        "updated_at": record.get("updated_at"),
        "document_type": record.get("document_type"),
        "content_type": record.get("content_type"),
        "title": record.get("title"),
        "url": record.get("url"),
        "document_url": record.get("document_url"),
        "source_url": source_trace.get("source_url"),
        "extraction_status": extraction_trace.get("status"),
        "access_status": extraction_trace.get("access_status") or record.get("access_status"),
    }


def _record_kind(record: dict[str, Any]) -> str:
    if record.get("document_type"):
        return "document"
    if record.get("precedent_type"):
        return "precedent"
    return "decision"


_CSV_FIELDS = [
    "record_kind",
    "id",
    "source",
    "court",
    "case_number",
    "registry_number",
    "decision_type",
    "precedent_type",
    "number",
    "case_class",
    "subject",
    "rapporteur",
    "judging_body",
    "origin_county",
    "judgment_date",
    "publication_date",
    "status",
    "updated_at",
    "document_type",
    "content_type",
    "title",
    "url",
    "document_url",
    "source_url",
    "extraction_status",
    "access_status",
]

_MARKDOWN_FIELDS = [
    ("ID", "id"),
    ("Fonte", "source"),
    ("Assunto", "subject"),
    ("Relator", "rapporteur"),
    ("Tipo de decisao", "decision_type"),
    ("Tipo de precedente", "precedent_type"),
    ("Data de julgamento", "judgment_date"),
    ("Data de publicacao", "publication_date"),
    ("Status", "status"),
    ("Titulo", "title"),
    ("URL", "url"),
    ("URL do documento", "document_url"),
]
