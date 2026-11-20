"""Ponto de entrada compatível com o script original."""

from agente_curriculo.agent import criar_agente
from agente_curriculo.cli import executar, ler_vaga_terminal
from agente_curriculo.github_tools import (
    buscar_meus_projetos_github as buscar_projetos_github,
    criar_cliente_github,
)
from agente_curriculo.google_docs import (
    obter_ou_criar_pasta,
    gerar_curriculo_no_docs,
    obter_credenciais_google
    
)
from agente_curriculo.models import DadosCurriculo
from agente_curriculo.settings import (
    GITHUB_TOKEN,
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SCOPES,
    LOCAL_TEMPLATE_PATH,
    # TEMPLATE_DOC_ID,
)


SCOPES = GOOGLE_SCOPES
gh = criar_cliente_github(GITHUB_TOKEN)
agente = criar_agente(gh)

def buscar_meus_projetos_github() -> str:
    """Compatibilidade para imports que usavam a tool diretamente."""
    return buscar_projetos_github(gh)


if __name__ == "__main__":
    executar()
