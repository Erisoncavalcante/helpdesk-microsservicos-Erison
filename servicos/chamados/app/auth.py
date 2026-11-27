"""Confere o token JWT.

Este serviço não tem a tabela de usuários: ele confia no que está dentro do
token (id e perfil), assinado pelo serviço de Usuários. O próprio token fica
guardado para ser repassado quando Chamados precisar chamar outro serviço.
"""
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import JWT_ALGORITMO, JWT_EMISSOR, JWT_SEGREDO

esquema = HTTPBearer(auto_error=False)

NAO_AUTENTICADO = HTTPException(
    status_code=401, detail="Faça login para continuar.", headers={"WWW-Authenticate": "Bearer"}
)


@dataclass
class UsuarioToken:
    id: int
    perfil: str
    token: str  # repassado no cabeçalho Authorization ao chamar Usuários e Inventário


def usuario_atual(credenciais: HTTPAuthorizationCredentials | None = Depends(esquema)) -> UsuarioToken:
    if credenciais is None or credenciais.scheme.lower() != "bearer":
        raise NAO_AUTENTICADO
    try:
        dados = jwt.decode(
            credenciais.credentials, JWT_SEGREDO, algorithms=[JWT_ALGORITMO], issuer=JWT_EMISSOR,
            options={"require": ["exp", "iat", "sub", "iss"]},
        )
        return UsuarioToken(id=int(dados["sub"]), perfil=dados["perfil"], token=credenciais.credentials)
    except (jwt.PyJWTError, ValueError, KeyError):
        raise NAO_AUTENTICADO
