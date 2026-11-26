"""Chamadas HTTP aos outros serviços (Usuários e Inventário).

Sempre repassam o token do usuário e nunca esperam mais que o timeout.
"""
import httpx
from fastapi import HTTPException

from app.config import TIMEOUT_SEGUNDOS, URL_INVENTARIO, URL_USUARIOS
from app.erros import NaoEncontrado, RegraDeNegocio, SemPermissao, ServicoIndisponivel

TIMEOUT = httpx.Timeout(TIMEOUT_SEGUNDOS, connect=2.0)


def _get(url: str, token: str, servico: str, msg_404: str) -> dict:
    try:
        r = httpx.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=TIMEOUT)
    except httpx.RequestError:  # serviço parado, sem rede ou estourou o timeout
        raise ServicoIndisponivel(f"O serviço de {servico} está indisponível. Tente novamente em instantes.")
    if r.status_code == 404:
        raise NaoEncontrado(msg_404)
    if r.status_code == 401:
        raise HTTPException(status_code=401, detail="Faça login para continuar.")
    if r.status_code == 403:
        raise SemPermissao(f"Sem permissão para consultar {servico}.")
    if r.status_code != 200:
        raise ServicoIndisponivel(f"O serviço de {servico} respondeu com erro. Tente novamente em instantes.")
    return r.json()


def obter_ativo(ativo_id: int, token: str) -> dict:
    return _get(f"{URL_INVENTARIO}/ativos/{ativo_id}", token, "inventário", f"Ativo {ativo_id} não encontrado.")


def obter_tecnico(usuario_id: int, token: str) -> dict:
    usuario = _get(f"{URL_USUARIOS}/usuarios/{usuario_id}", token, "usuários", f"Usuário {usuario_id} não encontrado.")
    if usuario["perfil"] != "tecnico":  # regra que antes vivia em usuarios.servico.obter_tecnico
        raise RegraDeNegocio(f"Usuário {usuario_id} não é técnico.")
    return usuario