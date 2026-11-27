"""Testes de segurança do serviço de Chamados: token, permissões e entrada."""
from datetime import datetime, timedelta, timezone

import jwt

from app import config
from tests.conftest import criar_token


def abrir(cliente, h, **extra):
    return cliente.post("/chamados", headers=h, json={"titulo": "Teste", "descricao": "Teste", "prioridade": "baixa", **extra})


# ---------- token ----------

def test_rotas_exigem_login(cliente):
    for metodo, rota in [("get", "/chamados"), ("get", "/chamados/1"), ("get", "/chamados/painel"),
                         ("get", "/notificacoes"), ("post", "/chamados")]:
        assert getattr(cliente, metodo)(rota).status_code == 401, rota


def test_token_adulterado(cliente, contas):
    token = contas["ana"]["headers"]["Authorization"] + "x"
    assert cliente.get("/chamados", headers={"Authorization": token}).status_code == 401


def test_token_assinado_com_outro_segredo(cliente):
    falso = criar_token(1, "admin", segredo="segredo-de-outra-pessoa-com-mais-de-32-caracteres")
    assert cliente.get("/chamados", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_sem_assinatura_alg_none(cliente):
    agora = datetime.now(timezone.utc)
    falso = jwt.encode({"sub": "1", "perfil": "admin", "iss": config.JWT_EMISSOR, "iat": agora,
                        "exp": agora + timedelta(hours=1)}, None, algorithm="none")
    assert cliente.get("/chamados", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_expirado(cliente):
    vencido = criar_token(2, "solicitante", minutos=-5)
    assert cliente.get("/chamados", headers={"Authorization": f"Bearer {vencido}"}).status_code == 401


def test_token_sem_perfil(cliente):
    agora = datetime.now(timezone.utc)
    sem_perfil = jwt.encode({"sub": "1", "iss": config.JWT_EMISSOR, "iat": agora, "exp": agora + timedelta(hours=1)},
                            config.JWT_SEGREDO, algorithm="HS256")
    assert cliente.get("/chamados", headers={"Authorization": f"Bearer {sem_perfil}"}).status_code == 401


# ---------- permissões ----------

def test_solicitante_nao_ve_chamado_de_outra_pessoa(cliente, contas):
    cid = abrir(cliente, contas["ana"]["headers"]).json()["id"]
    assert cliente.get(f"/chamados/{cid}", headers=contas["bia"]["headers"]).status_code == 404
    assert cliente.get("/chamados", headers=contas["bia"]["headers"]).json() == []


def test_solicitante_nao_atribui_nem_resolve(cliente, contas):
    cid = abrir(cliente, contas["ana"]["headers"]).json()["id"]
    h = contas["ana"]["headers"]
    assert cliente.patch(f"/chamados/{cid}/atribuir", headers=h, json={"tecnico_id": contas["carla"]["id"]}).status_code == 403
    assert cliente.patch(f"/chamados/{cid}/status", headers=h, json={"status": "em_atendimento"}).status_code == 403


def test_nao_da_para_abrir_chamado_em_nome_de_outro(cliente, contas):
    r = abrir(cliente, contas["ana"]["headers"], solicitante_id=contas["bia"]["id"])
    assert r.status_code == 422


def test_nao_da_para_comentar_em_nome_de_outro(cliente, contas):
    cid = abrir(cliente, contas["ana"]["headers"]).json()["id"]
    r = cliente.post(f"/chamados/{cid}/comentarios", headers=contas["ana"]["headers"],
                     json={"texto": "oi", "autor_id": contas["carla"]["id"]})
    assert r.status_code == 422


def test_notificacoes_sao_so_do_proprio_usuario(cliente, contas):
    abrir(cliente, contas["ana"]["headers"])
    assert cliente.get("/notificacoes", headers=contas["bia"]["headers"]).json() == []


# ---------- entrada ----------

def test_titulo_grande_demais(cliente, contas):
    assert abrir(cliente, contas["ana"]["headers"], titulo="x" * 500).status_code == 422


def test_requisicao_grande_demais(cliente, contas):
    corpo = '{"titulo": "' + "x" * 70000 + '"}'
    r = cliente.post("/chamados", headers={**contas["ana"]["headers"], "Content-Type": "application/json"}, content=corpo)
    assert r.status_code == 413


def test_texto_com_html_e_guardado_como_texto(cliente, contas):
    r = abrir(cliente, contas["ana"]["headers"], titulo="<script>alert(1)</script>")
    assert r.status_code == 201 and r.json()["titulo"] == "<script>alert(1)</script>"
