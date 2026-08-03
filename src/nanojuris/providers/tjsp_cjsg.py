"""TJSP CJSG public jurisprudence provider."""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from nanojuris.config import NanoJurisConfig
from nanojuris.errors import (
    AccessControlRequiredError,
    ParserContractChangedError,
    RateLimitDetectedError,
    SourceUnavailableError,
)
from nanojuris.models import (
    AccessStatus,
    CanonicalDocument,
    DecisionBundle,
    ExtractionTrace,
    JurisprudenceQuery,
    JurisprudenceResult,
    ProviderCapabilities,
    SearchPage,
    SourceTrace,
)
from nanojuris.providers.base import JurisprudenceProvider


@dataclass(slots=True, frozen=True)
class CjsgAccessDiagnostic:
    """Access and response-shape signals observed in TJSP/CJSG HTML."""

    has_result_container: bool
    has_download_links: bool
    has_search_form: bool
    has_recaptcha_field: bool
    has_uuid_captcha_field: bool
    has_recaptcha_widget: bool
    has_access_control_route: bool
    has_login_script: bool

    @property
    def access_control_required(self) -> bool:
        return not self.has_result_container and (
            self.has_recaptcha_field
            or self.has_uuid_captcha_field
            or self.has_recaptcha_widget
            or self.has_access_control_route
        )

    @property
    def returned_to_search_form(self) -> bool:
        return self.has_search_form and not self.has_result_container

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)

    def summary(self) -> str:
        flags = [name for name, value in self.to_dict().items() if value]
        return ", ".join(flags) if flags else "no known TJSP/CJSG access signals"


class TjspCjsgProvider(JurisprudenceProvider):
    """Provider for the public TJSP CJSG jurisprudence search."""

    name = "tjsp_cjsg"

    def __init__(
        self,
        config: NanoJurisConfig | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.config = config or NanoJurisConfig()
        self.session = session or requests.Session()
        self._last_request = 0.0

    def search(self, query: JurisprudenceQuery) -> SearchPage:
        endpoint = "/resultadoCompleta.do"
        payload = self._build_payload(query)
        html = self._request_text("POST", endpoint, data=payload)
        trace = SourceTrace(
            provider=self.name,
            endpoint=endpoint,
            query=payload,
            source_url=urljoin(self.config.tjsp_cjsg_url.rstrip("/") + "/", endpoint.lstrip("/")),
            limitations=[
                "Fonte HTML publica do TJSP/CJSG sujeita a mudancas de layout.",
                "O provider detecta captcha/controle de acesso e nao implementa bypass.",
                (
                    "Inteiro teor e acessivel apenas quando a fonte publica "
                    "disponibiliza cdAcordao/cdForo."
                ),
            ],
        )
        return parse_cjsg_results(
            html,
            query=query,
            trace=trace,
            base_url=self.config.tjsp_cjsg_url,
        )

    def get_decisions(self, precedent_id: str) -> DecisionBundle:
        cd_acordao, cd_foro = self._parse_precedent_id(precedent_id)
        endpoint = f"/getArquivo.do?cdAcordao={cd_acordao}&cdForo={cd_foro}"
        content = self._request_text("GET", endpoint)
        trace = SourceTrace(
            provider=self.name,
            endpoint="/getArquivo.do",
            query={"cdAcordao": cd_acordao, "cdForo": cd_foro},
            source_url=urljoin(self.config.tjsp_cjsg_url.rstrip("/") + "/", endpoint.lstrip("/")),
            limitations=[
                "O retorno pode ser HTML, PDF ou uma tela de controle de acesso da propria fonte.",
            ],
        )
        return DecisionBundle(
            precedent_id=precedent_id,
            source=self.name,
            texts=[{"content": content, "content_type": "text/html"}],
            source_trace=trace,
            raw={"cd_acordao": cd_acordao, "cd_foro": cd_foro},
        )

    def get_document(self, document_id: str) -> CanonicalDocument:
        cd_acordao, cd_foro = self._parse_precedent_id(document_id)
        bundle = self.get_decisions(document_id)
        content = str(bundle.texts[0].get("content") if bundle.texts else "")
        content_type = str(bundle.texts[0].get("content_type") if bundle.texts else "text/html")
        content_bytes = content.encode("utf-8")
        return CanonicalDocument(
            id=document_id,
            source=self.name,
            document_type="acordao",
            content_type=content_type,
            title=f"TJSP/CJSG inteiro teor {document_id}",
            text=content,
            url=bundle.source_trace.source_url if bundle.source_trace else None,
            sha256=hashlib.sha256(content_bytes).hexdigest(),
            byte_size=len(content_bytes),
            retrieved_at=bundle.source_trace.retrieved_at if bundle.source_trace else None,
            access_status=AccessStatus.PUBLIC,
            source_trace=bundle.source_trace,
            extraction_trace=ExtractionTrace(
                parser="tjsp_cjsg.get_document",
                parser_version="1",
                content_sha256=hashlib.sha256(content_bytes).hexdigest(),
                content_bytes=len(content_bytes),
                metadata={"cd_acordao": cd_acordao, "cd_foro": cd_foro},
            ),
            raw_metadata={"cd_acordao": cd_acordao, "cd_foro": cd_foro},
        )

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            source=self.name,
            display_name="TJSP Consulta de Jurisprudencia/CJSG",
            source_url=self.config.tjsp_cjsg_url,
            category="court_jurisprudence",
            search_modes=["full_text", "summary", "case_number", "date_range", "decision_type"],
            document_types=["acordao", "monocratic_decision", "homologation"],
            content_formats=["html"],
            canonical_records=["CanonicalDecision", "CanonicalDocument"],
            extracted_fields=[
                "case_number",
                "decision_type",
                "case_class",
                "subject",
                "rapporteur",
                "origin_county",
                "judging_body",
                "publication_date",
                "summary",
                "document_url",
                "cd_acordao",
                "cd_foro",
                "access_diagnostic_flags",
            ],
            access_statuses=[
                AccessStatus.PUBLIC,
                AccessStatus.PARTIAL,
                AccessStatus.ACCESS_CONTROL_REQUIRED,
                AccessStatus.SOURCE_UNAVAILABLE,
            ],
            endpoints=[
                "POST /resultadoCompleta.do",
                "GET /getArquivo.do?cdAcordao=<id>&cdForo=<foro>",
            ],
            supports_full_text=True,
            supports_catalog=False,
            supports_suggestions=False,
            supports_live_tests=True,
            limitations=[
                "A fonte pode exigir captcha ou outro controle de acesso.",
                "Inteiro teor depende de cdAcordao/cdForo publico e da resposta da fonte.",
                (
                    "O provider diagnostica sinais de formulario, reCAPTCHA, "
                    "uuidCaptcha e login sem bypass."
                ),
            ],
            responsible_use=[
                "Nao tentar contornar captcha, login ou controles de acesso.",
                "Usar testes live apenas quando explicitamente habilitados.",
            ],
        )

    def _build_payload(self, query: JurisprudenceQuery) -> dict[str, str | list[str]]:
        decision_types = query.types or ["A"]
        mapped_types = [self._map_decision_type(item) for item in decision_types]
        return {
            "conversationId": "",
            "dados.buscaInteiroTeor": query.text,
            "dados.pesquisarComSinonimos": ["S", "S"],
            "dados.buscaEmenta": query.exact_phrase,
            "dados.nuProcOrigem": query.number,
            "dados.nuRegistro": "",
            "agenteSelectedEntitiesList": "",
            "contadoragente": "0",
            "contadorMaioragente": "0",
            "codigoCr": "",
            "codigoTr": "",
            "nmAgente": "",
            "juizProlatorSelectedEntitiesList": "",
            "contadorjuizProlator": "0",
            "contadorMaiorjuizProlator": "0",
            "codigoJuizCr": "",
            "codigoJuizTr": "",
            "nmJuiz": "",
            "classesTreeSelection.values": "",
            "classesTreeSelection.text": "",
            "assuntosTreeSelection.values": "",
            "assuntosTreeSelection.text": "",
            "comarcaSelectedEntitiesList": "",
            "contadorcomarca": "0",
            "contadorMaiorcomarca": "0",
            "cdComarca": "",
            "nmComarca": "",
            "secoesTreeSelection.values": "",
            "secoesTreeSelection.text": "",
            "dados.dtJulgamentoInicio": query.updated_from,
            "dados.dtJulgamentoFim": query.updated_to,
            "dados.dtPublicacaoInicio": "",
            "dados.dtPublicacaoFim": "",
            "dados.origensSelecionadas": "T",
            "tipoDecisaoSelecionados": mapped_types,
            "dados.ordenarPor": self._map_order_by(query.order_by),
        }

    def _request_text(self, method: str, path: str, **kwargs: Any) -> str:
        self._respect_rate_limit()
        url = urljoin(self.config.tjsp_cjsg_url.rstrip("/") + "/", path.lstrip("/"))
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": self.config.user_agent,
        }
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=self.config.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise SourceUnavailableError(f"TJSP/CJSG request failed: {exc}") from exc

        if response.status_code == 429:
            raise RateLimitDetectedError("TJSP/CJSG returned HTTP 429")
        if response.status_code >= 500:
            raise SourceUnavailableError(f"TJSP/CJSG returned HTTP {response.status_code}")
        if response.status_code >= 400:
            raise SourceUnavailableError(
                f"TJSP/CJSG rejected request with HTTP {response.status_code}"
            )
        response.encoding = response.encoding or "utf-8"
        text = response.text
        diagnostic = diagnose_cjsg_access(text)
        if diagnostic.access_control_required:
            raise AccessControlRequiredError(
                "TJSP/CJSG requires captcha or another access-control step "
                f"({diagnostic.summary()})"
            )
        return text

    def _respect_rate_limit(self) -> None:
        interval = self.config.rate_limit_interval
        if interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request
        if elapsed < interval:
            time.sleep(interval - elapsed)
        self._last_request = time.monotonic()

    @staticmethod
    def _map_decision_type(value: str) -> str:
        normalized = value.strip().lower()
        mapping = {
            "a": "A",
            "acordao": "A",
            "acórdão": "A",
            "m": "M",
            "monocratica": "M",
            "monocrática": "M",
            "h": "H",
            "homologacao": "H",
            "homologação": "H",
        }
        return mapping.get(normalized, value.upper())

    @staticmethod
    def _map_order_by(value: str) -> str:
        normalized = value.strip().lower()
        mapping = {
            "text": "dtPublicacao",
            "relevance": "dtPublicacao",
            "dtpublicacao": "dtPublicacao",
            "publication": "dtPublicacao",
            "date": "dtPublicacao",
        }
        return mapping.get(normalized, value or "dtPublicacao")

    @staticmethod
    def _parse_precedent_id(precedent_id: str) -> tuple[str, str]:
        match = re.fullmatch(r"tjsp-cjsg-(?P<cd>\d+)(?:-(?P<foro>\d+))?", precedent_id)
        if not match:
            raise ParserContractChangedError(
                "TJSP/CJSG precedent id must look like tjsp-cjsg-<cdAcordao>-<cdForo>"
            )
        return match.group("cd"), match.group("foro") or "0"


def parse_cjsg_results(
    html: str,
    *,
    query: JurisprudenceQuery,
    trace: SourceTrace,
    base_url: str,
    source: str = "tjsp_cjsg",
    court: str = "TJSP",
    id_prefix: str = "tjsp-cjsg",
    source_label: str = "TJSP/CJSG",
) -> SearchPage:
    """Parse a CJSG result page into normalized results."""

    if _looks_like_access_control(html):
        raise AccessControlRequiredError(f"{source_label} returned captcha/access-control HTML")

    soup = BeautifulSoup(html, "html.parser")
    result_root = soup.select_one("#divDadosResultado-A") or soup.select_one("#tdResultados")
    if result_root is None:
        if "Resultado consulta" in html or "Resultados" in html:
            return SearchPage(
                source=source,
                total=0,
                start=0,
                end=0,
                page=query.page,
                page_size=query.page_size,
                results=[],
                source_trace=trace,
            )
        raise ParserContractChangedError(f"{source_label} result container not found")

    total, start, end = _parse_pagination(soup.get_text(" ", strip=True))
    results: list[JurisprudenceResult] = []
    seen: set[tuple[str, str]] = set()
    for anchor in result_root.select("a.downloadEmenta"):
        cd_acordao = str(anchor.get("cdacordao") or anchor.get("cdAcordao") or "")
        cd_foro = str(anchor.get("cdforo") or anchor.get("cdForo") or "0")
        key = (cd_acordao, cd_foro)
        if not cd_acordao or key in seen:
            continue
        case_number = anchor.get_text(" ", strip=True)
        if not case_number:
            continue
        seen.add(key)
        container = anchor.find_parent("table")
        if container is None:
            continue
        labels = _extract_labeled_fields(container)
        summary = _extract_summary(container, cd_acordao)
        class_subject = labels.get("classe/assunto")
        case_class, subject = _split_class_subject(class_subject)
        full_text_url = urljoin(
            base_url.rstrip("/") + "/",
            f"getArquivo.do?cdAcordao={cd_acordao}&cdForo={cd_foro}",
        )
        result_trace = SourceTrace(
            provider=trace.provider,
            endpoint="/resultadoCompleta.do",
            query=trace.query,
            source_url=full_text_url,
            limitations=trace.limitations,
        )
        result = JurisprudenceResult(
            id=f"{id_prefix}-{cd_acordao}-{cd_foro}",
            source=source,
            court=court,
            type="acordao",
            number=case_number,
            summary=summary,
            rapporteur=labels.get("relator(a)") or labels.get("relator"),
            updated_at=labels.get("data de registro") or labels.get("data de publicação"),
            highlights={},
            source_trace=result_trace,
            raw={
                "cd_acordao": cd_acordao,
                "cd_foro": cd_foro,
                "full_text_url": full_text_url,
                "classe": case_class,
                "assunto": subject,
                "comarca": labels.get("comarca"),
                "orgao_julgador": labels.get("órgão julgador") or labels.get("orgao julgador"),
                "labels": labels,
            },
        )
        results.append(result)

    if not results and total > 0:
        raise ParserContractChangedError(f"{source_label} parser found total results but no items")
    limited_results = results[: query.page_size]

    return SearchPage(
        source=source,
        total=total or len(results),
        start=start or (1 if results else 0),
        end=(start or 1) + len(limited_results) - 1 if limited_results else 0,
        page=query.page,
        page_size=query.page_size,
        results=limited_results,
        source_trace=trace,
    )


def _parse_pagination(text: str) -> tuple[int, int, int]:
    match = re.search(r"Resultados\s+(\d+)\s+a\s+(\d+)\s+de\s+(\d+)", text, re.I)
    if not match:
        return 0, 0, 0
    start, end, total = (int(match.group(index)) for index in (1, 2, 3))
    return total, start, end


def _extract_labeled_fields(container: Any) -> dict[str, str]:
    labels: dict[str, str] = {}
    for row in container.select("tr.ementaClass2"):
        strong = row.find("strong")
        if strong is None:
            continue
        label = _normalize_label(strong.get_text(" ", strip=True))
        full_text = row.get_text(" ", strip=True)
        value = full_text.replace(strong.get_text(" ", strip=True), "", 1).strip(" :\xa0")
        if label and value:
            labels[label] = value
    text = container.get_text("\n", strip=True)
    for label in ("Data de Registro", "Data de Publicação", "Data de julgamento"):
        match = re.search(rf"{label}\s*:\s*(\d{{2}}/\d{{2}}/\d{{4}})", text, re.I)
        if match:
            labels[_normalize_label(label)] = match.group(1)
    return labels


def _extract_summary(container: Any, cd_acordao: str) -> str | None:
    text_area = container.select_one(f"#textAreaDados_{cd_acordao}")
    if text_area is not None:
        return text_area.get_text(" ", strip=True) or None
    candidates = [
        row.get_text(" ", strip=True) for row in container.select("tr.ementaClass, tr.ementaClass2")
    ]
    joined = " ".join(candidates)
    return joined or None


def _split_class_subject(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    if "/" not in value:
        return value.strip(), None
    case_class, subject = value.split("/", 1)
    return case_class.strip(), subject.strip()


def _normalize_label(label: str) -> str:
    return re.sub(r"\s+", " ", label.replace(":", "")).strip().lower()


def _looks_like_access_control(html: str) -> bool:
    return diagnose_cjsg_access(html).access_control_required


def diagnose_cjsg_access(html: str) -> CjsgAccessDiagnostic:
    """Classify public TJSP/CJSG response signals without solving access controls."""

    lowered = html.lower()
    return CjsgAccessDiagnostic(
        has_result_container="divdadosresultado" in lowered or "tdresultados" in lowered,
        has_download_links="downloadementa" in lowered,
        has_search_form="consultacompletaform" in lowered or "consultasimplesform" in lowered,
        has_recaptcha_field="recaptcha_response_token" in lowered,
        has_uuid_captcha_field="uuidcaptcha" in lowered,
        has_recaptcha_widget="g-recaptcha" in lowered,
        has_access_control_route="captchacontroleacesso" in lowered,
        has_login_script="verificarlogin" in lowered or "sajcas" in lowered,
    )
