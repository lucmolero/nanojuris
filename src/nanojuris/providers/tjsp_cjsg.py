"""TJSP CJSG public jurisprudence provider."""

from __future__ import annotations

import re
import time
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
    DecisionBundle,
    JurisprudenceQuery,
    JurisprudenceResult,
    SearchPage,
    SourceTrace,
)
from nanojuris.providers.base import JurisprudenceProvider


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
        if _looks_like_access_control(text):
            raise AccessControlRequiredError(
                "TJSP/CJSG requires captcha or another access-control step"
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
) -> SearchPage:
    """Parse a CJSG result page into normalized results."""

    if _looks_like_access_control(html):
        raise AccessControlRequiredError("TJSP/CJSG returned captcha/access-control HTML")

    soup = BeautifulSoup(html, "html.parser")
    result_root = soup.select_one("#divDadosResultado-A") or soup.select_one("#tdResultados")
    if result_root is None:
        if "Resultado consulta" in html or "Resultados" in html:
            return SearchPage(
                source="tjsp_cjsg",
                total=0,
                start=0,
                end=0,
                page=query.page,
                page_size=query.page_size,
                results=[],
                source_trace=trace,
            )
        raise ParserContractChangedError("TJSP/CJSG result container not found")

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
            id=f"tjsp-cjsg-{cd_acordao}-{cd_foro}",
            source="tjsp_cjsg",
            court="TJSP",
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
        raise ParserContractChangedError("TJSP/CJSG parser found total results but no items")

    return SearchPage(
        source="tjsp_cjsg",
        total=total or len(results),
        start=start or (1 if results else 0),
        end=end or len(results),
        page=query.page,
        page_size=query.page_size,
        results=results,
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
    lowered = html.lower()
    if "divdadosresultado" in lowered or "tdresultados" in lowered:
        return False
    if "g-recaptcha" in lowered or "recaptcha_response_token" in lowered:
        return True
    if "captcha" in lowered and "resultado consulta" not in lowered:
        return True
    return False
