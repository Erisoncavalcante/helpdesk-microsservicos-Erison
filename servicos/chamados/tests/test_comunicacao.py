"""Comunicação com os outros serviços: token repassado, timeout e falhas (erro 503)."""


def abrir_com_equipamento(cliente, contas):
    return cliente.post("/chamados", headers=contas["ana"]["headers"],
                        json={"titulo": "PC não liga", "descricao": "Nada acontece", "prioridade": "alta", "ativo_id": 1})


def test_confere_o_equipamento_no_inventario_repassando_o_token(cliente, contas, rede):
    assert abrir_com_equipamento(cliente, contas).status_code == 201
    url, cabecalhos = rede.chamadas[-1]
    assert url.endswith("/ativos/1")
    assert cabecalhos["Authorization"] == contas["ana"]["headers"]["Authorization"]


def test_inventario_fora_do_ar_responde_503(cliente, contas, rede):
    rede.fora_do_ar.add("inventario")
    r = abrir_com_equipamento(cliente, contas)
    assert r.status_code == 503 and "fora do ar" in r.json()["detail"]


def test_inventario_lento_responde_503(cliente, contas, rede):
    rede.lentos.add("inventario")
    r = abrir_com_equipamento(cliente, contas)
    assert r.status_code == 503 and "demorou" in r.json()["detail"]


def test_sem_inventario_o_resto_continua_funcionando(cliente, contas, rede):
    rede.fora_do_ar.add("inventario")
    # chamado SEM equipamento não depende do Inventário
    r = cliente.post("/chamados", headers=contas["ana"]["headers"],
                     json={"titulo": "Sem acesso", "descricao": "Preciso de acesso", "prioridade": "baixa"})
    assert r.status_code == 201
    assert cliente.get("/chamados", headers=contas["ana"]["headers"]).status_code == 200


def test_usuarios_fora_do_ar_ao_atribuir_responde_503(cliente, contas, rede):
    cid = abrir_com_equipamento(cliente, contas).json()["id"]
    rede.fora_do_ar.add("usuarios")
    r = cliente.patch(f"/chamados/{cid}/atribuir", headers=contas["carla"]["headers"], json={"tecnico_id": 4})
    assert r.status_code == 503
    # e o chamado não muda
    assert cliente.get(f"/chamados/{cid}", headers=contas["carla"]["headers"]).json()["status"] == "aberto"
