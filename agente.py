import os
from dotenv import load_dotenv
from github import Auth, Github
from openai import OpenAI
from groq import Groq
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
gh = Github(auth=Auth.Token(GITHUB_TOKEN))

modelo_groq = OpenAIChatModel(
    "openai/gpt-oss-120b",
    provider=OpenAIProvider(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
    ),
)

modelo_resiliente = FallbackModel(
    "google:gemini-3.8-flash",
    "google:gemini-3.5-flash-lite",
    modelo_groq
)

# Definir a estrutura exata dos campos do currículo
class DadosCurriculo(BaseModel):
    cargo_alvo: str = Field(
        description="Título profissional alinhado à vaga, ex: Desenvolvedor Back-End | Java & Spring Boot"
    )
    resumo: str = Field(
        description="Resumo de 3 a 4 linhas conectando a experiência na Health-Connect e projetos à vaga"
    )

    proj_1_titulo: str
    proj_1_link: str
    proj_1_bullet_1: str
    proj_1_bullet_2: str
    proj_1_bullet_3: str

    proj_2_titulo: str
    proj_2_link: str
    proj_2_bullet_1: str
    proj_2_bullet_2: str
    proj_2_bullet_3: str

    skills_linguagens: str
    skills_frameworks: str
    skills_bancos: str
    skills_ferramentas: str


# Configurar o Agente
agente = Agent(
    modelo_resiliente,
    model_settings=ModelSettings(timeout=60),
    output_type=DadosCurriculo,
    system_prompt=(
        "Você é um especialista em recrutamento de TI. Sua missão é ler a descrição "
        "de uma vaga de estágio e adaptar o currículo do candidato.\n"
        "Regras obrigatórias:\n"
        "1. Sempre chame a ferramenta 'buscar_meus_projetos_github' antes de responder.\n"
        "2. Use apenas dados reais encontrados nos repositórios e na experiência do candidato na Health-Connect (React, Next.js, TypeScript, Node.js, Express, MongoDB).\n"
        "3. Nunca invente tecnologias ou projetos que não existam."
    ),
)

# Ferramenta para ler apenas repositórios marcados com o topic 'portfolio'
@agente.tool_plain
def buscar_meus_projetos_github() -> str:
    #Busca apenas os repositórios marcados com o tópico 'portfolio' e lê os READMEs.
    print("-> [Tool] Consultando repositórios no GitHub...")
    repos = gh.get_user().get_repos(visibility="public")
    projetos_filtrados = []

    for repo in repos:
        if repo.fork or "portfolio" not in repo.get_topics():
            continue

        try:
            readme = repo.get_readme().decoded_content.decode("utf-8")[:2000]
        except Exception:
            readme = "Sem README disponível."

        info = (
            f"=== PROJETO: {repo.name} ===\n"
            f"URL: {repo.html_url}\n"
            f"Linguagem principal: {repo.language}\n"
            f"Descrição: {repo.description}\n"
            f"Resumo do README:\n{readme}\n"
        )
        projetos_filtrados.append(info)

    if not projetos_filtrados:
        return "Nenhum repositório encontrado com o tópico 'portfolio'."

    return "\n".join(projetos_filtrados)


# Execução do teste
if __name__ == "__main__":
    vaga_teste = """
    Vaga: Estágio em Desenvolvimento Back-End
    Requisitos: Conhecimento em Java, Spring Boot, criação de APIs REST e bancos relacionais (MySQL ou PostgreSQL).
    Diferencial: Docker, Git e testes automatizados.
    """

    # teste = Agent(modelo_reserva)
    # print(teste.run_sync("Diga olá!"). output)

    print("Analisando vaga e gerando adaptação...")
    resultado = agente.run_sync(f"Adapte meu currículo para esta vaga:\n{vaga_teste}")

    # Exibe o resultado estruturado no terminal
    dados = resultado.output
    print("\n=== RESULTADO GERADO ===")
    print(f"Cargo Alvo: {dados.cargo_alvo}\n")
    print(f"Resumo:\n{dados.resumo}\n")
    print(f"Projeto 1: {dados.proj_1_titulo} ({dados.proj_1_link})")
    print(f"  * {dados.proj_1_bullet_1}")
    print(f"  * {dados.proj_1_bullet_2}")
    print(f"  * {dados.proj_1_bullet_3}\n")
    print(f"Projeto 2: {dados.proj_2_titulo} ({dados.proj_2_link})")
    print(f"  * {dados.proj_2_bullet_1}")
    print(f"  * {dados.proj_2_bullet_2}")
    print(f"  * {dados.proj_2_bullet_3}\n")
    print(f"Linguagens: {dados.skills_linguagens}")
    print(f"Frameworks: {dados.skills_frameworks}")
    print(f"Bancos: {dados.skills_bancos}")
    print(f"Ferramentas: {dados.skills_ferramentas}")