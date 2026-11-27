"""Configurações do serviço de Chamados (lidas das variáveis de ambiente)."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chamados.db")

# O segredo PRECISA ser o mesmo em todos os serviços, senão um não aceita o token do outro.
JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
if len(JWT_SEGREDO) < 32:
    raise RuntimeError("Defina JWT_SEGREDO no arquivo .env (mínimo 32 caracteres).")

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"

# Onde estão os outros serviços (dentro do Docker, cada um se chama pelo nome)
URL_USUARIOS = os.getenv("URL_USUARIOS", "http://usuarios:8000")
URL_INVENTARIO = os.getenv("URL_INVENTARIO", "http://inventario:8000")
# Tempo máximo esperando a resposta de outro serviço
TIMEOUT_SEGUNDOS = float(os.getenv("TIMEOUT_SEGUNDOS", "3"))

TAMANHO_MAXIMO_REQUISICAO = 64 * 1024
DOCS_ATIVA = os.getenv("DOCS", "1") == "1"
