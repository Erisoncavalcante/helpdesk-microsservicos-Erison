"""Configurações do serviço de Chamados, lidas das variáveis de ambiente."""
import os

# Cada serviço tem o seu próprio banco
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chamados.db")

# Mesmo segredo dos outros serviços, vindo do ambiente (.env). Aqui só confere tokens.
JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
if len(JWT_SEGREDO) < 32:
    raise RuntimeError("Defina JWT_SEGREDO com pelo menos 32 caracteres (veja o .env.example).")

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"

# Endereços dos outros serviços (dentro do Docker, pelo nome do serviço)
URL_USUARIOS = os.environ["URL_USUARIOS"]
URL_INVENTARIO = os.environ["URL_INVENTARIO"]

# Quanto tempo esperar por outro serviço antes de desistir (segundos)
TIMEOUT_SEGUNDOS = float(os.getenv("TIMEOUT_SEGUNDOS", "3"))

# Tamanho máximo do corpo de uma requisição (em bytes)
TAMANHO_MAXIMO_REQUISICAO = 64 * 1024

DOCS_ATIVA = os.getenv("DOCS", "1") == "1"