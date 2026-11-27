"""Configurações do gateway (lidas das variáveis de ambiente)."""
import os

# Endereço de cada serviço DENTRO do Docker (os serviços se chamam pelo nome, não por localhost)
SERVICOS = {
    "usuarios": os.getenv("URL_USUARIOS", "http://usuarios:8000"),
    "inventario": os.getenv("URL_INVENTARIO", "http://inventario:8000"),
    # Chamados também guarda as notificações
    "chamados": os.getenv("URL_CHAMADOS", "http://chamados:8000"),
}

# Qual serviço atende cada rota (pelo primeiro pedaço do caminho)
ROTAS = {
    "auth": "usuarios",
    "usuarios": "usuarios",
    "ativos": "inventario",
    "chamados": "chamados",
    "notificacoes": "chamados",
}

# Tempo máximo esperando a resposta de um serviço
TIMEOUT_SEGUNDOS = float(os.getenv("TIMEOUT_SEGUNDOS", "5"))

TAMANHO_MAXIMO_REQUISICAO = 64 * 1024
