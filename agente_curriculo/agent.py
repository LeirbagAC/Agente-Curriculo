from dataclasses import dataclass
from pathlib import Path

from github import Github
from pydantic_ai import Agent, ModelSettings, PromptedOutput, RunContext
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .github_tools import buscar_meus_projetos_github as buscar_projetos
from .models import DadosCurriculo
from .settings import GROQ_API_KEY

# Define as definições de contexto para o agente do perfil do candidato
@dataclass
class ContextoCandidato:
    perfil_markdown: str

def carregar_perfil(caminho: str = "perfil.md") -> str:
    """Lê o arquivo de perfil do candidato ou orienta a criação a partir do exemplo."""
    arquivo = Path(caminho)
    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo '{caminho}' não encontrado. "
            "Copie 'perfil.example.md' para 'perfil.md' e preencha com seus dados."
        )
    return arquivo.read_text(encoding="utf-8")

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

    # Prompt estático focado apenas em regras de comportamento e formato ATS
    agente = Agent(
        modelo_resiliente,
        deps_type=ContextoCandidato,
        model_settings=ModelSettings(timeout=60),
        output_type=PromptedOutput(DadosCurriculo),
        system_prompt=(
            "Você é um especialista em recrutamento técnico (ATS) e redação de currículos para estágio em TI.\n\n"
            "### REGRAS DE VERACIDADE\n"
            "1. Chame sempre a ferramenta 'buscar_meus_projetos_github' antes de gerar o currículo.\n"
            "2. Use EXCLUSIVAMENTE fatos, tecnologias e métricas presentes no 'PERFIL DO CANDIDATO' e nos READMEs retornados.\n"
            "3. Se a vaga pedir uma tecnologia que o candidato não possui (ex: AWS, C#, Kubernetes), apenas omita sem inventar.\n"
            "4. Nunca invente porcentagens, quantidades de usuários ou tempos de experiência. Nunca escreva colchetes como [PREENCHER].\n"
            "5. Gere o currículo no mesmo idioma da descrição da vaga.\n\n"
            "### FÓRMULA OBRIGATÓRIA DOS BULLETS\n"
            "Cada bullet de projeto DEVE seguir a estrutura: [Verbo de ação no passado] + [escopo técnico e ferramentas] + [resultado concreto ou ganho operacional].\n"
            "- Quando houver métrica real no perfil/README (ex: 'taxa de descarga (%/h)', 'antecipando em semanas'), use-a.\n"
            "- Quando não houver número, use o resultado técnico verificável (ex: 'padronizando o ambiente de execução', 'garantindo integridade dos dados').\n\n"
            "### EXEMPLOS DE ESTILO ESPERADO (FEW-SHOT)\n"
            "- Bom bullet: 'Implementei autenticação e autorização por papéis (USER, SELLER e ADMIN) com Spring Security e JWT, restringindo cada perfil aos recursos autorizados.'\n"
            "- Bom bullet: 'Automatizei a análise de telemetria com pandas e matplotlib, calculando taxa de descarga (%/h) e gerando relatórios em Markdown prontos para ciclos de teste.'\n"
            "### EXEMPLOS DE RESUMO POR TIPO DE VAGA (USE COMO REFERÊNCIA DE RITMO, NÃO COPIE LITERALMENTE)\n"
            "- Para vaga de QA / Automação: 'Estudante do 7º período de Sistemas de Informação com vivência prática na startup Health-Connect, atuando na validação de fluxos web e integração com APIs REST. Possui experiência em automação de testes unitários e de integração com Python e pytest, além de coleta e análise de métricas operacionais via ADB e pandas. Busca estágio em Qualidade de Software para aplicar testes automatizados e inglês avançado (C1) na garantia de confiabilidade de sistemas.'\n"
            "- Para vaga de Back-End: 'Estudante do 7º período de Sistemas de Informação com experiência na startup Health-Connect desenvolvendo APIs REST em Node.js e MongoDB e integrando aplicações web em TypeScript. Possui base sólida em desenvolvimento back-end com Java, Spring Boot, autenticação JWT, modelagem relacional em MySQL e conteinerização com Docker. Busca estágio em Desenvolvimento Back-End para construir serviços escaláveis e bem estruturados.'\n"
    ),
)

    # Injeta o conteúdo do perfil.md dinamicamente no contexto do modelo
    @agente.system_prompt
    def adicionar_contexto_candidato(ctx: RunContext[ContextoCandidato]) -> str:
        return f"=== PERFIL DO CANDIDATO ===\n{ctx.deps.perfil_markdown}"

    @agente.tool_plain
    def buscar_meus_projetos_github() -> str:
        """Busca apenas os repositórios marcados com o tópico 'portfolio' e lê os READMEs."""
        return buscar_projetos(gh)

    return agente
