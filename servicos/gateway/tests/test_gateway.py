"""Testes do API Gateway: encaminhamento, token, falhas e segurança da tela."""
from pathlib import Path

import pytest


@pytest.mark.parametrize("rota, servico", [
    ("/auth/login", "usuarios"), ("/usuarios/4", "usuarios"), ("/ativos", "inventario"),
    ("/chamados/painel", "chamados"), ("/notificacoes", "chamados"),
])
def test_encaminha_para_o_servico_certo(cliente, rota, servico):
    r = cliente.get(rota)
    assert r.status_code == 200 and r.json() == {"servico": servico, "caminho": rota}


def test_repassa_o_token_e_a_consulta(cliente, servicos):
    cliente.get("/ativos", params={"setor": "TI"}, headers={"Authorization": "Bearer abc"})
    enviada = servicos.recebidas[-1]
    assert enviada.headers["authorization"] == "Bearer abc"
    assert enviada.url.params["setor"] == "TI"


def test_nao_aceita_ip_falsificado(cliente, servicos):
    cliente.post("/auth/login", json={}, headers={"X-Forwarded-For": "1.2.3.4"})
    assert servicos.recebidas[-1].headers["x-forwarded-for"] != "1.2.3.4"


def test_servico_fora_do_ar_responde_503(cliente, servicos):
    servicos.fora_do_ar.add("inventario")
    r = cliente.get("/ativos")
    assert r.status_code == 503 and "fora do ar" in r.json()["detail"]
    # os outros serviços continuam respondendo
    assert cliente.get("/chamados").status_code == 200


def test_saude_mostra_quem_esta_fora_do_ar(cliente, servicos):
    assert cliente.get("/saude").status_code == 200
    servicos.fora_do_ar.add("inventario")
    r = cliente.get("/saude")
    assert r.status_code == 503 and r.json()["servicos"]["inventario"] == "fora do ar"


def test_rota_desconhecida(cliente):
    assert cliente.get("/qualquer-coisa").status_code == 404


def test_requisicao_grande_demais(cliente):
    r = cliente.post("/chamados", content="x" * 70000, headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_tela_escapa_o_html():
    js = (Path(__file__).parent.parent / "app" / "web" / "app.js").read_text(encoding="utf-8")
    assert "const esc =" in js and "onclick" not in js


def test_cabecalhos_de_seguranca(cliente):
    r = cliente.get("/")
    assert "script-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
