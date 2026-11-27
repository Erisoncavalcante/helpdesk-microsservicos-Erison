"""Usuários de exemplo (só para aula). Desligue com DADOS_EXEMPLO=0."""
import os

from sqlalchemy.orm import Session

from app.usuarios import servico as usuarios
from app.usuarios.esquemas import UsuarioCriar

SENHA = os.getenv("SENHA_EXEMPLO", "Helpdesk2026")


def carregar(db: Session) -> None:
    if usuarios.listar(db):
        return
    # Criados nesta ordem, ficam com os ids 1 a 5 (o serviço de Chamados usa esses ids)
    for nome, email, perfil in [
        ("Admin TI", "admin@empresa.com", "admin"),          # id 1
        ("Ana Souza", "ana@empresa.com", "solicitante"),     # id 2
        ("Bruno Lima", "bruno@empresa.com", "solicitante"),  # id 3
        ("Carla Dias", "carla@empresa.com", "tecnico"),      # id 4
        ("Diego Rocha", "diego@empresa.com", "tecnico"),     # id 5
    ]:
        usuarios.criar(db, UsuarioCriar(nome=nome, email=email, perfil=perfil, senha=SENHA))
