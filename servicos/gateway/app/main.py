"""API Gateway: o único ponto de entrada do HelpDesk.

A tela e todas as requisições chegam aqui (porta 8000) e o gateway repassa
cada uma para o serviço certo, olhando o começo do caminho (/auth, /ativos...).
"""
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from app.config import ROTAS, SERVICOS, TIMEOUT_SEGUNDOS
from app.seguranca_http import CabecalhosDeSeguranca

WEB = Path(__file__).parent / "web"

# Cabeçalhos que valem só para uma conexão e não devem ser repassados
NAO_REPASSAR = {
    "host", "connection", "keep-alive", "transfer-encoding", "content-length", "content-encoding",
    "upgrade", "te", "trailer", "proxy-authorization", "proxy-authenticate", "x-forwarded-for",
}


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    # Um cliente HTTP só, reaproveitado em todas as requisições
    app.state.cliente = httpx.AsyncClient(timeout=TIMEOUT_SEGUNDOS)
    yield
    await app.state.cliente.aclose()


app = FastAPI(title="HelpDesk TI · Gateway", lifespan=ciclo_de_vida, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CabecalhosDeSeguranca)


# ---------- Tela do HelpDesk (servida pelo próprio gateway) ----------

@app.get("/", include_in_schema=False)
def tela_inicial():
    return FileResponse(WEB / "index.html")


@app.get("/app.js", include_in_schema=False)
def script():
    return FileResponse(WEB / "app.js", media_type="text/javascript")


@app.get("/estilo.css", include_in_schema=False)
def estilo():
    return FileResponse(WEB / "estilo.css", media_type="text/css")


# ---------- Saúde: mostra quais serviços estão no ar ----------

@app.get("/saude")
async def saude(request: Request):
    situacao = {}
    for nome, url in SERVICOS.items():
        try:
            r = await request.app.state.cliente.get(f"{url}/saude", timeout=2)
            situacao[nome] = "no ar" if r.status_code == 200 else f"erro {r.status_code}"
        except httpx.HTTPError:
            situacao[nome] = "fora do ar"
    tudo_ok = all(v == "no ar" for v in situacao.values())
    return JSONResponse(status_code=200 if tudo_ok else 503, content={"gateway": "no ar", "servicos": situacao})


# ---------- Encaminhamento: repassa a requisição para o serviço certo ----------

@app.api_route("/{caminho:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def encaminhar(caminho: str, request: Request):
    nome = ROTAS.get(caminho.split("/", 1)[0])
    if nome is None:
        return JSONResponse(status_code=404, content={"detail": "Rota não encontrada."})

    # Repassa os cabeçalhos (inclusive Authorization, o token do usuário)
    cabecalhos = {k: v for k, v in request.headers.items() if k.lower() not in NAO_REPASSAR}
    # Informa o IP real de quem chamou (o limite de tentativas de login usa esse IP).
    # O valor que veio do cliente é descartado, para ninguém conseguir falsificar o IP.
    cabecalhos["x-forwarded-for"] = request.client.host if request.client else ""

    try:
        resposta = await request.app.state.cliente.request(
            request.method, f"{SERVICOS[nome]}/{caminho}",
            params=list(request.query_params.multi_items()),
            content=await request.body(), headers=cabecalhos,
        )
    except httpx.TimeoutException:
        return JSONResponse(status_code=503, content={"detail": f"O serviço de {nome} demorou para responder. Tente de novo."})
    except httpx.HTTPError:
        return JSONResponse(status_code=503, content={"detail": f"O serviço de {nome} está fora do ar. Tente de novo em instantes."})

    saida = {k: v for k, v in resposta.headers.items() if k.lower() not in NAO_REPASSAR}
    return Response(content=resposta.content, status_code=resposta.status_code, headers=saida)
