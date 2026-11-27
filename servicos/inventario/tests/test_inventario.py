"""Testes do serviço de Inventário, incluindo a segurança (token e permissões)."""
from datetime import datetime, timedelta, timezone

import jwt

from app import config
from tests.conftest import criar_token

ATIVO = {"patrimonio": "PAT-1", "tipo": "computador", "descricao": "Desktop", "setor": "TI"}


def test_saude(cliente):
    assert cliente.get("/saude").json() == {"status": "ok", "servico": "inventario"}


def test_rotas_exigem_login(cliente):
    for metodo, rota in [("get", "/ativos"), ("get", "/ativos/1"), ("post", "/ativos")]:
        assert getattr(cliente, metodo)(rota).status_code == 401, rota


def test_token_assinado_com_outro_segredo(cliente):
    falso = criar_token(1, "admin", segredo="segredo-de-outra-pessoa-com-mais-de-32-caracteres")
    assert cliente.get("/ativos", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_expirado(cliente):
    vencido = criar_token(1, "admin", minutos=-5)
    assert cliente.get("/ativos", headers={"Authorization": f"Bearer {vencido}"}).status_code == 401


def test_token_sem_assinatura_alg_none(cliente):
    agora = datetime.now(timezone.utc)
    falso = jwt.encode({"sub": "1", "perfil": "admin", "iss": config.JWT_EMISSOR, "iat": agora,
                        "exp": agora + timedelta(hours=1)}, None, algorithm="none")
    assert cliente.get("/ativos", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_adulterado(cliente, contas):
    assert cliente.get("/ativos", headers={"Authorization": contas["ana"]["Authorization"] + "x"}).status_code == 401


def test_solicitante_nao_cadastra_ativo(cliente, contas):
    assert cliente.post("/ativos", headers=contas["ana"], json=ATIVO).status_code == 403


def test_tecnico_cadastra_ativo_e_filtra_por_setor(cliente, contas):
    h = contas["carla"]
    cliente.post("/ativos", headers=h, json={"patrimonio": "PAT-1", "tipo": "impressora", "descricao": "HP", "setor": "RH"})
    cliente.post("/ativos", headers=h, json={"patrimonio": "PAT-2", "tipo": "computador", "descricao": "Dell", "setor": "TI"})
    assert len(cliente.get("/ativos", params={"setor": "RH"}, headers=h).json()) == 1


def test_patrimonio_repetido_e_recusado(cliente, contas):
    assert cliente.post("/ativos", headers=contas["carla"], json=ATIVO).status_code == 201
    assert cliente.post("/ativos", headers=contas["carla"], json=ATIVO).status_code == 422


def test_ativo_inexistente(cliente, contas):
    # O serviço de Chamados depende deste 404 para saber que o equipamento não existe
    assert cliente.get("/ativos/99", headers=contas["ana"]).status_code == 404


def test_requisicao_grande_demais(cliente, contas):
    corpo = '{"descricao": "' + "x" * 70000 + '"}'
    r = cliente.post("/ativos", headers={**contas["carla"], "Content-Type": "application/json"}, content=corpo)
    assert r.status_code == 413
