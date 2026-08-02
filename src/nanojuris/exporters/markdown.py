"""Markdown exporter."""

from __future__ import annotations

from nanojuris.models import JurisprudenceResult, SearchPage


def result_to_markdown(result: JurisprudenceResult) -> str:
    """Render one result as Markdown."""

    title = f"{result.court} {result.type}"
    if result.number is not None:
        title += f" {result.number}"

    lines = [f"## {title}", ""]
    lines.append(f"- ID: `{result.id}`")
    if result.status:
        lines.append(f"- Situacao: {result.status}")
    if result.updated_at:
        lines.append(f"- Atualizacao: {result.updated_at}")
    if result.rapporteur:
        lines.append(f"- Relator: {result.rapporteur}")

    if result.question:
        lines.extend(["", "### Questao", "", result.question])
    if result.thesis:
        lines.extend(["", "### Tese", "", result.thesis])
    if result.summary:
        lines.extend(["", "### Resumo", "", result.summary])
    if result.paradigm_cases:
        lines.extend(["", "### Processos paradigma"])
        for case in result.paradigm_cases:
            label = case.number
            if case.case_class:
                label += f" ({case.case_class})"
            if case.url:
                label += f" - {case.url}"
            lines.append(f"- {label}")

    if result.source_trace:
        lines.extend(["", "### Fonte", ""])
        lines.append(f"- Provider: `{result.source_trace.provider}`")
        lines.append(f"- Endpoint: `{result.source_trace.endpoint}`")
        lines.append(f"- Coletado em: `{result.source_trace.retrieved_at}`")

    return "\n".join(lines)


def search_page_to_markdown(page: SearchPage) -> str:
    """Render a search page as Markdown."""

    lines = [
        f"# Resultados NanoJuris ({page.source})",
        "",
        f"Total: {page.total}",
        f"Pagina: {page.page}",
        "",
    ]
    for result in page.results:
        lines.append(result_to_markdown(result))
        lines.append("")
    return "\n".join(lines).strip()
