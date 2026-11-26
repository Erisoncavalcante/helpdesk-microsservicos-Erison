"""Validação dos tokens JWT emitidos pelo serviço de Usuários."""
from dataclasses import dataclass

import jwt

from app.config import JWT_ALGORITMO, JWT_EMISSOR, JWT_SEGREDO


class TokenInvalido(Exception):
    pass


@dataclass
class Identidade:
    """Quem está chamando, segundo o token. Não existe tabela de usuários neste serviço."""
    id: int
    perfil: str


def ler(token: str) -> Identidade:
    """Devolve a identidade do token, ou lança TokenInvalido."""
    try:
        dados = jwt.decode(
            token, JWT_SEGREDO, algorithms=[JWT_ALGORITMO], issuer=JWT_EMISSOR,
            options={"require": ["exp", "iat", "sub", "iss"]},
        )
        return Identidade(id=int(dados["sub"]), perfil=dados["perfil"])
    except (jwt.PyJWTError, ValueError, KeyError) as erro:
        raise TokenInvalido() from erro