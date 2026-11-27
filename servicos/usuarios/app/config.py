"""Configurações do serviço de Usuários (lidas das variáveis de ambiente)."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./usuarios.db")

# O segredo PRECISA ser o mesmo em todos os serviços, senão um não aceita o token do outro.
# Por isso ele vem do .env e o serviço se recusa a subir sem ele.
JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
if len(JWT_SEGREDO) < 32:
    raise RuntimeError("Defina JWT_SEGREDO no arquivo .env (mínimo 32 caracteres).")

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"
TOKEN_MINUTOS = int(os.getenv("TOKEN_MINUTOS", "60"))

# Proteção contra tentativas de adivinhar senhas
LOGIN_MAX_FALHAS = int(os.getenv("LOGIN_MAX_FALHAS", "5"))
LOGIN_JANELA_SEGUNDOS = int(os.getenv("LOGIN_JANELA_SEGUNDOS", "300"))

TAMANHO_MAXIMO_REQUISICAO = 64 * 1024
DOCS_ATIVA = os.getenv("DOCS", "1") == "1"
