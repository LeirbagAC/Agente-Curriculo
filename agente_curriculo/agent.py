from github import Github
from pydantic_ai import Agent, ModelSettings, PromptedOutput
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .github_tools import buscar_meus_projetos_github as buscar_projetos
from .models import DadosCurriculo
from .settings import GROQ_API_KEY


def criar_agente(gh: Github) -> Agent:
    modelo_groq = OpenAIChatModel(
        "openai/gpt-oss-120b",
        provider=OpenAIProvider(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY,
        ),
    )

    modelo_resiliente = FallbackModel(
        "google:gemini-3.8-flash",
        "google:gemini-3.5-flash-lite",
        modelo_groq,
        "groq:qwen/qwen3.8-27b",
    )

    agente = Agent(
        modelo_resiliente,
        model_settings=ModelSettings(timeout=60),
        output_type=PromptedOutput(DadosCurriculo),
        system_prompt=(
            "Você é um especialista em recrutamento de TI e otimização ATS. Sua missão é ler a descrição "
            "de uma vaga de estágio e adaptar o currículo do candidato.\n"
            "Regras obrigatórias:\n"
            "1. Sempre chame a ferramenta 'buscar_meus_projetos_github' antes de responder.\n"
            "2. Use apenas dados reais encontrados nos repositórios e na experiência do candidato na Health-Connect "
            "(React, Next.js, TypeScript, Node.js, Express.js, MongoDB).\n"
            "3. Nunca invente tecnologias, métricas ou projetos que não existam.\n"
            "4. Escreva bullets técnicos diretos começando com verbos de ação no passado (ex: Desenvolvi, Implementei, Modelei)."
        ),
    )

    @agente.tool_plain
    def buscar_meus_projetos_github() -> str:
        """Busca apenas os repositórios marcados com o tópico 'portfolio' e lê os READMEs."""
        return buscar_projetos(gh)

    return agente
