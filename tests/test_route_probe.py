from __future__ import annotations

import pytest

from nanojuris.route_probe import (
    analyze_route_response,
    parse_json_object,
    parse_key_value_pairs,
)


def test_analyze_route_response_marks_legal_html_as_live_valid():
    html = """
    <html>
      <head><title>Pesquisa de Jurisprudencia</title></head>
      <body>
        <p>Processo 0000001-10.2024.8.26.0100</p>
        <p>Acórdão. Ementa. Relator Fulano. Órgão julgador: 1a Câmara.</p>
        <a href="/documento.pdf">Inteiro teor</a>
        <a href="?pagina=2">Próxima</a>
      </body>
    </html>
    """

    result = analyze_route_response(
        url="https://example.test/jurisprudencia",
        final_url="https://example.test/jurisprudencia",
        method="GET",
        status_code=200,
        content=html.encode(),
        content_type="text/html; charset=utf-8",
        expected_texts=["Acórdão"],
        elapsed_ms=120,
    )

    assert result.ok is True
    assert result.route_status == "live_valid"
    assert result.quality_grade == "A"
    assert result.legal_signals["case_number"] is True
    assert result.route_features["pagination"] is True
    assert result.route_features["full_text_link"] is True


def test_analyze_route_response_blocks_access_control_html():
    html = """
    <html>
      <body>
        <form>captcha</form>
        <script src="https://www.google.com/recaptcha/api.js"></script>
        <p>Faça login para entrar no sistema.</p>
      </body>
    </html>
    """

    result = analyze_route_response(
        url="https://example.test/bloqueado",
        final_url="https://example.test/bloqueado",
        method="GET",
        status_code=200,
        content=html.encode(),
        content_type="text/html",
    )

    assert result.ok is False
    assert result.route_status == "access_control_or_login"
    assert result.quality_grade == "D"
    assert result.access_signals["captcha"] is True
    assert result.access_signals["recaptcha"] is True
    assert "nao implementar bypass" in result.recommendation.lower()


def test_analyze_route_response_classifies_captcha_401_as_access_control():
    html = (
        "<html><title>Informe o código</title><body>Captcha Digite os números abaixo</body></html>"
    )

    result = analyze_route_response(
        url="https://example.test/jurisprudencia/pesquisa",
        final_url="https://example.test/jurisprudencia/pesquisa",
        method="GET",
        status_code=401,
        content=html.encode(),
        content_type="text/html",
    )

    assert result.ok is False
    assert result.route_status == "access_control_or_login"
    assert result.access_signals["captcha"] is True


def test_analyze_route_response_does_not_block_public_page_with_login_icon():
    html = """
    <html>
      <body>
        <nav>Icone de Login Intranet Webmail</nav>
        <main>Consulta à Jurisprudência eproc decisão</main>
      </body>
    </html>
    """

    result = analyze_route_response(
        url="https://example.test/consulta",
        final_url="https://example.test/consulta",
        method="GET",
        status_code=200,
        content=html.encode(),
        content_type="text/html",
        expected_texts=["eproc"],
    )

    assert result.route_status == "live_valid"
    assert result.access_signals["login"] is False


def test_analyze_route_response_does_not_block_global_recaptcha_script():
    html = """
    <html>
      <head><script src="https://www.google.com/recaptcha/api.js"></script></head>
      <body>
        <main>
          Busca de Jurisprudência
          Resultado da pesquisa
          Ementa decisão relator órgão julgador inteiro teor
        </main>
      </body>
    </html>
    """

    result = analyze_route_response(
        url="https://example.test/jurisprudencia",
        final_url="https://example.test/jurisprudencia",
        method="GET",
        status_code=200,
        content=html.encode(),
        content_type="text/html",
        expected_texts=["Resultado da pesquisa"],
    )

    assert result.route_status == "live_valid"
    assert result.access_signals["recaptcha"] is False


def test_analyze_route_response_does_not_block_global_turnstile_assets():
    html = """
    <html>
      <body>
        <main>
          <p>1357643 resultados encontrados para o filtro da pesquisa</p>
          <p>Processo 5730482-09.2026.8.09.0051. Ementa. Relator.</p>
          <a>Baixar Inteiro teor</a>
        </main>
        <!-- src="https://challenges.cloudflare.com/turnstile/v0/api.js" -->
        <script>const label = "cloudflare turnstile";</script>
      </body>
    </html>
    """

    result = analyze_route_response(
        url="https://example.test/jurisprudencia",
        final_url="https://example.test/jurisprudencia",
        method="POST",
        status_code=200,
        content=html.encode(),
        content_type="text/html",
        expected_texts=["resultados encontrados"],
    )

    assert result.route_status == "live_valid"
    assert result.access_signals["turnstile"] is False
    assert result.access_signals["cloudflare"] is False


def test_analyze_route_response_blocks_cloudflare_challenge_page():
    html = """
    <html>
      <head><title>Just a moment...</title></head>
      <body>
        Enable JavaScript and cookies to continue.
        Cloudflare Ray ID: abc123
        <script src="/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1"></script>
      </body>
    </html>
    """

    result = analyze_route_response(
        url="https://example.test/jurisprudencia",
        final_url="https://example.test/jurisprudencia",
        method="GET",
        status_code=403,
        content=html.encode(),
        content_type="text/html",
    )

    assert result.route_status == "access_control_or_login"
    assert result.access_signals["cloudflare"] is True


def test_analyze_route_response_scores_structured_json_candidate():
    body = b'{"items":[{"numero":"0000001-10.2024.8.26.0100","ementa":"IDPJ"}]}'

    result = analyze_route_response(
        url="https://api.example.test/search",
        final_url="https://api.example.test/search",
        method="POST",
        status_code=200,
        content=body,
        content_type="application/json",
        expected_texts=["IDPJ"],
        elapsed_ms=80,
    )

    assert result.ok is True
    assert result.route_features["structured_response"] is True
    assert result.legal_signals["case_number"] is True
    assert result.score >= 8


def test_analyze_route_response_marks_404_as_not_found():
    result = analyze_route_response(
        url="https://example.test/missing",
        final_url="https://example.test/missing",
        method="GET",
        status_code=404,
        content=b"Not found",
        content_type="text/plain",
    )

    assert result.ok is False
    assert result.route_status == "not_found"
    assert result.quality_grade == "D"


def test_parse_key_value_pairs_accepts_form_payload():
    assert parse_key_value_pairs(["dados.buscaInteiroTeor=idpj", "pagina=1"]) == {
        "dados.buscaInteiroTeor": "idpj",
        "pagina": "1",
    }


def test_parse_key_value_pairs_rejects_invalid_payload():
    with pytest.raises(ValueError, match="chave=valor"):
        parse_key_value_pairs(["idpj"])


def test_parse_json_object_accepts_only_objects():
    assert parse_json_object('{"q":"idpj"}') == {"q": "idpj"}
    with pytest.raises(ValueError, match="objeto"):
        parse_json_object('["idpj"]')
