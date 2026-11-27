"""Equipamentos de exemplo (só para aula). Desligue com DADOS_EXEMPLO=0."""
from sqlalchemy.orm import Session

from app import servico
from app.esquemas import AtivoCriar


def carregar(db: Session) -> None:
    if servico.listar(db):
        return
    # Criados nesta ordem, ficam com os ids 1, 2 e 3 (o serviço de Chamados usa esses ids)
    servico.criar(db, AtivoCriar(patrimonio="PAT-0001", tipo="computador", descricao="Desktop Dell OptiPlex", setor="Financeiro"))
    servico.criar(db, AtivoCriar(patrimonio="PAT-0002", tipo="impressora", descricao="Impressora HP LaserJet", setor="RH"))
    servico.criar(db, AtivoCriar(patrimonio="PAT-0003", tipo="notebook", descricao="Notebook Lenovo ThinkPad", setor="TI"))
