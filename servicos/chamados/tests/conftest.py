"""Configuração dos testes do serviço de Chamados.

- Os tokens são criados aqui, como se tivessem vindo do serviço de Usuários.
- Os serviços de Usuários e Inventário são trocados por uma "rede falsa": assim
  dá para testar o que acontece quando eles respondem, não encontram o recurso,
  estão fora do ar ou demoram (timeout), sem precisar subir os outros serviços.
"""
import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("JWT_SEGREDO", "segredo-so-para-os-testes-com-mais-de-32-caracteres")
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["DADOS_EXEMPLO"] = "0"

import httpx  # noqa: E402
import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import clientes, config  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

# O que os serviços de Usuários e Inventário "sabem" nesta rede falsa
USUARIOS = {
    1: {"id": 1, "nome": "Admin", "perfil": "admin"},
    2: {"id": 2, "nome": "Ana", "perfil": "solicitante"},
    3: {"id": 3, "nome": "Bia", "perfil": "solicitante"},
    4: {"id": 4, "nome": "Carla", "perfil": "tecnico"},
}
ATIVOS = {1: {"id": 1, "patrimonio": "PAT-1", "tipo": "computador", "descricao": "Desktop", "setor": "TI"}}


def criar_token(usuario_id: int, perfil: str, segredo: str = config.JWT_SEGREDO, minutos: int = 60) -> str:
    agora = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(usuario_id), "perfil": perfil, "iss": config.JWT_EMISSOR, "iat": agora,
                       "exp": agora + timedelta(minutes=minutos)}, segredo, algorithm="HS256")


class RedeFalsa:
    """Substitui o httpx.get usado em clientes.py."""

    def __init__(self):
        self.fora_do_ar: set[str] = set()   # ex.: {"inventario"}
        self.lentos: set[str] = set()       # ex.: {"usuarios"} -> timeout
        self.chamadas: list[tuple[str, dict]] = []

    def get(self, url, headers=None, timeout=None):
        self.chamadas.append((url, headers or {}))
        servico = "inventario" if "/ativos/" in url else "usuarios"
        requisicao = httpx.Request("GET", url)
        if servico in self.fora_do_ar:
            raise httpx.ConnectError("conexão recusada", request=requisicao)
        if servico in self.lentos:
            raise httpx.ReadTimeout("demorou demais", request=requisicao)
        dados = (ATIVOS if servico == "inventario" else USUARIOS).get(int(url.rsplit("/", 1)[1]))
        if dados is None:
            return httpx.Response(404, json={"detail": "não encontrado"}, request=requisicao)
        return httpx.Response(200, json=dados, request=requisicao)


@pytest.fixture
def rede(monkeypatch):
    falsa = RedeFalsa()
    monkeypatch.setattr(clientes.httpx, "get", falsa.get)
    return falsa


@pytest.fixture
def cliente(rede):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def db_de_teste():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = db_de_teste
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def contas():
    resultado = {}
    for apelido, usuario_id in [("admin", 1), ("ana", 2), ("bia", 3), ("carla", 4)]:
        token = criar_token(usuario_id, USUARIOS[usuario_id]["perfil"])
        resultado[apelido] = {"headers": {"Authorization": f"Bearer {token}"}, "id": usuario_id}
    return resultado
