"""Configurações do serviço de Usuários, lidas das variáveis de ambiente."""
import os

# Cada serviço tem o seu próprio banco
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/usuarios.db")

# Segredo que assina os tokens JWT. Tem de ser o MESMO em todos os serviços
# e vem sempre do ambiente (.env): sem ele, o serviço não sobe.
JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
if len(JWT_SEGREDO) < 32:
    raise RuntimeError("Defina JWT_SEGREDO com pelo menos 32 caracteres (veja o .env.example).")

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"
TOKEN_MINUTOS = int(os.getenv("TOKEN_MINUTOS", "60"))

# Proteção contra tentativas de adivinhar senhas
LOGIN_MAX_FALHAS = int(os.getenv("LOGIN_MAX_FALHAS", "5"))
LOGIN_JANELA_SEGUNDOS = int(os.getenv("LOGIN_JANELA_SEGUNDOS", "300"))

# Tamanho máximo do corpo de uma requisição (em bytes)
TAMANHO_MAXIMO_REQUISICAO = 64 * 1024

DOCS_ATIVA = os.getenv("DOCS", "1") == "1"