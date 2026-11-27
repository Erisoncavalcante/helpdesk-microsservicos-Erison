"""Configurações do serviço de Inventário (lidas das variáveis de ambiente)."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventario.db")

# O segredo PRECISA ser o mesmo em todos os serviços, senão um não aceita o token do outro.
# Por isso ele vem do .env e o serviço se recusa a subir sem ele.
JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
if len(JWT_SEGREDO) < 32:
    raise RuntimeError("Defina JWT_SEGREDO no arquivo .env (mínimo 32 caracteres).")

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"

TAMANHO_MAXIMO_REQUISICAO = 64 * 1024
DOCS_ATIVA = os.getenv("DOCS", "1") == "1"
