"""Configuração dos testes do serviço de Inventário.

Este serviço não tem usuários: os testes criam tokens assinados com o mesmo
segredo, como se tivessem vindo do serviço de Usuários.
"""
import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("JWT_SEGREDO", "segredo-so-para-os-testes-com-mais-de-32-caracteres")
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["DADOS_EXEMPLO"] = "0"

import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import config  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


def criar_token(usuario_id: int, perfil: str, segredo: str = config.JWT_SEGREDO, minutos: int = 60) -> str:
    agora = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(usuario_id), "perfil": perfil, "iss": config.JWT_EMISSOR, "iat": agora,
                       "exp": agora + timedelta(minutes=minutos)}, segredo, algorithm="HS256")


@pytest.fixture
def cliente():
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
    return {apelido: {"Authorization": f"Bearer {criar_token(i, perfil)}"}
            for i, (apelido, perfil) in enumerate([("admin", "admin"), ("ana", "solicitante"), ("carla", "tecnico")], start=1)}
