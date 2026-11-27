"""Configuração dos testes do gateway.

Os serviços de verdade são trocados por um "transporte falso" do httpx, que
anota cada requisição recebida e responde como se fosse o serviço.
"""
import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app


class ServicosFalsos:
    def __init__(self):
        self.recebidas: list[httpx.Request] = []
        self.fora_do_ar: set[str] = set()  # nomes dos hosts, ex.: {"inventario"}

    def responder(self, requisicao: httpx.Request) -> httpx.Response:
        self.recebidas.append(requisicao)
        if requisicao.url.host in self.fora_do_ar:
            raise httpx.ConnectError("conexão recusada", request=requisicao)
        if requisicao.url.path == "/saude":
            return httpx.Response(200, json={"status": "ok"})
        return httpx.Response(200, json={"servico": requisicao.url.host, "caminho": requisicao.url.path})


@pytest.fixture
def servicos():
    return ServicosFalsos()


@pytest.fixture
def cliente(servicos):
    with TestClient(app) as c:
        # troca o cliente HTTP do gateway por um que fala com os serviços falsos
        app.state.cliente = httpx.AsyncClient(transport=httpx.MockTransport(servicos.responder))
        yield c
