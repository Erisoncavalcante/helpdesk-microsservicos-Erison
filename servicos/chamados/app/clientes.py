"""Chamadas HTTP para os outros serviços.

No monólito, isto era uma chamada de função (usuarios.obter_tecnico, inventario.obter).
Agora passa pela rede, então pode demorar ou falhar: por isso o timeout e o erro 503.
"""
import httpx

from app.config import TIMEOUT_SEGUNDOS, URL_INVENTARIO, URL_USUARIOS
from app.erros import NaoEncontrado, RegraDeNegocio, ServicoIndisponivel


def _buscar(servico: str, url: str, token: str) -> dict | None:
    """Faz um GET repassando o token do usuário. Devolve None se o recurso não existir."""
    try:
        resposta = httpx.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=TIMEOUT_SEGUNDOS)
    except httpx.TimeoutException:
        raise ServicoIndisponivel(f"O serviço de {servico} demorou para responder. Tente de novo em instantes.")
    except httpx.HTTPError:
        raise ServicoIndisponivel(f"O serviço de {servico} está fora do ar. Tente de novo em instantes.")
    if resposta.status_code == 404:
        return None
    if resposta.status_code != 200:
        raise ServicoIndisponivel(f"O serviço de {servico} respondeu com erro {resposta.status_code}.")
    return resposta.json()


def obter_ativo(ativo_id: int, token: str) -> dict:
    ativo = _buscar("inventário", f"{URL_INVENTARIO}/ativos/{ativo_id}", token)
    if ativo is None:
        raise NaoEncontrado(f"Ativo {ativo_id} não encontrado.")
    return ativo


def obter_tecnico(usuario_id: int, token: str) -> dict:
    usuario = _buscar("usuários", f"{URL_USUARIOS}/usuarios/{usuario_id}", token)
    if usuario is None:
        raise NaoEncontrado(f"Usuário {usuario_id} não encontrado.")
    if usuario["perfil"] != "tecnico":
        raise RegraDeNegocio(f"Usuário {usuario_id} não é técnico.")
    return usuario
