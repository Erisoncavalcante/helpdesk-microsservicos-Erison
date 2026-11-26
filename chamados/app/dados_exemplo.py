"""Cria os chamados de exemplo quando o banco está vazio (uso apenas em aula).

Grava direto no banco deste serviço, sem chamar os outros. Usa os ids dos seeds
dos outros serviços: usuários 2=Ana, 3=Bruno, 4=Carla; ativos 1=computador, 2=impressora.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.chamados import repositorio, servico
from app.chamados.modelos import Chamado
from app.notificacoes import servico as notificacoes

ANA, BRUNO, CARLA = 2, 3, 4


def carregar(db: Session) -> None:
    if repositorio.listar(db):
        return
    agora = datetime.now()

    def abrir(titulo, descricao, prioridade, solicitante_id, ativo_id=None) -> Chamado:
        chamado = repositorio.salvar(db, Chamado(
            titulo=titulo, descricao=descricao, prioridade=prioridade, status="aberto",
            solicitante_id=solicitante_id, ativo_id=ativo_id, criado_em=agora,
            prazo_sla=servico.calcular_prazo(prioridade, agora),
        ))
        notificacoes.notificar(
            db, "ChamadoAberto", solicitante_id,
            f"Seu chamado #{chamado.id} foi aberto. Prazo: {chamado.prazo_sla:%d/%m %H:%M}.",
        )
        return chamado

    c1 = abrir("Computador não liga", "Apertei o botão e nada acontece.", "alta", ANA, 1)
    abrir("Impressora atolando papel", "Atola a cada 3 folhas.", "media", BRUNO, 2)
    abrir("Acesso ao sistema de RH", "Preciso de acesso para a nova estagiária.", "baixa", BRUNO)

    c1.tecnico_id = CARLA
    c1.status = "em_atendimento"
    repositorio.salvar(db, c1)
    notificacoes.notificar(db, "ChamadoAtribuido", CARLA, f"O chamado #{c1.id} foi atribuído a você.")