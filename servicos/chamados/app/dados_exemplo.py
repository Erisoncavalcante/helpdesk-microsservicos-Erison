"""Chamados de exemplo (só para aula). Desligue com DADOS_EXEMPLO=0.

Os ids vêm dos dados de exemplo dos outros serviços:
usuários 2 = Ana, 3 = Bruno, 4 = Carla (técnica); ativos 1 = desktop, 2 = impressora.
Aqui os chamados são gravados direto no banco, sem chamar os outros serviços,
porque na hora em que este serviço sobe eles podem ainda não estar no ar.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.chamados import repositorio
from app.chamados.modelos import Chamado
from app.chamados.servico import calcular_prazo
from app.notificacoes import servico as notificacoes

ANA, BRUNO, CARLA = 2, 3, 4
DESKTOP, IMPRESSORA = 1, 2


def carregar(db: Session) -> None:
    if db.scalar(select(Chamado).limit(1)):
        return
    agora = datetime.now()

    def novo(titulo, descricao, prioridade, solicitante, ativo=None, tecnico=None):
        chamado = repositorio.salvar(db, Chamado(
            titulo=titulo, descricao=descricao, prioridade=prioridade, solicitante_id=solicitante,
            ativo_id=ativo, tecnico_id=tecnico, status="em_atendimento" if tecnico else "aberto",
            criado_em=agora, prazo_sla=calcular_prazo(prioridade, agora),
        ))
        notificacoes.notificar(db, "ChamadoAberto", solicitante,
                               f"Seu chamado #{chamado.id} foi aberto. Prazo: {chamado.prazo_sla:%d/%m %H:%M}.")
        if tecnico:
            notificacoes.notificar(db, "ChamadoAtribuido", tecnico, f"O chamado #{chamado.id} foi atribuído a você.")

    novo("Computador não liga", "Apertei o botão e nada acontece.", "alta", ANA, DESKTOP, tecnico=CARLA)
    novo("Impressora atolando papel", "Atola a cada 3 folhas.", "media", BRUNO, IMPRESSORA)
    novo("Acesso ao sistema de RH", "Preciso de acesso para a nova estagiária.", "baixa", BRUNO)
