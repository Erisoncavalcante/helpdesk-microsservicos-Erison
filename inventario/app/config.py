"""Configurações do serviço de Inventário, lidas das variáveis de ambiente."""
import os

# Cada serviço tem o seu próprio banco
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/inventario.db")

# Mesmo segredo do serviço de Usuários, vindo do ambiente (.env).
# Aqui ele só serve para CONFERIR tokens; quem emite é o serviço de Usuários.
JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
if len(JWT_SEGREDO) < 32:
    raise RuntimeError("Defina JWT_SEGREDO com pelo menos 32 caracteres (veja o .env.example).")

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"

# Tamanho máximo do corpo de uma requisição (em bytes)
TAMANHO_MAXIMO_REQUISICAO = 64 * 1024

DOCS_ATIVA = os.getenv("DOCS", "1") == "1"