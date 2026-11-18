import os
from dotenv import load_dotenv
from github import Auth, Github

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelSettings, PromptedOutput
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")
TEMPLATE_DOC_ID = os.getenv("TEMPLATE_DOC_ID")
#GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID") #ID da pasta no Google Drive onde o novo currículo será salvo 

gh = Github(auth=Auth.Token(GITHUB_TOKEN))

# Configurar modelos e cadeia de Fallback
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
    modelo_groq,
    "groq:qwen/qwen3.8-27b",
)


# Schema de saída estruturada espelhando os placeholders do Google Docs
class DadosCurriculo(BaseModel):
    nome_arquivo: str = Field(
        description="Nome curto sem espaços especiais para salvar no Drive, ex: CV_Gabriel_Backend_EmpresaX"
    )
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


# Tool para ler repositórios marcados com o topic 'portfolio'
@agente.tool_plain
def buscar_meus_projetos_github() -> str:
    """Busca apenas os repositórios marcados com o tópico 'portfolio' e lê os READMEs."""
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


# Integração com Google Drive & Google Docs API
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",  # Permite ler/copiar o template existente
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]


def obter_credenciais_google() -> Credentials:
    """Autentica via OAuth 2.0 do usuário e salva/renova o token.json localmente."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def gerar_curriculo_no_docs(dados: DadosCurriculo) -> str:
    """Duplica o template no seu Google Drive e substitui todos os placeholders no Google Docs."""
    creds = obter_credenciais_google()

    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    # Passo A: Duplicar o template direto no seu Google Drive
    copy_body = {"name": dados.nome_arquivo}
    #if GOOGLE_DRIVE_FOLDER_ID:
    #    copy_body["parents"] = [GOOGLE_DRIVE_FOLDER_ID]

    copia = (
        drive_service.files()
        .copy(fileId=TEMPLATE_DOC_ID, body=copy_body)
        .execute()
    )
    novo_doc_id = copia.get("id")

    # Passo B: Mapear placeholders para os valores gerados
    substituicoes = {
        "{{CARGO_ALVO}}": dados.cargo_alvo,
        "{{RESUMO}}": dados.resumo,
        "{{PROJ_1_TITULO}}": dados.proj_1_titulo,
        "{{PROJ_1_LINK}}": dados.proj_1_link,
        "{{PROJ_1_BULLET_1}}": dados.proj_1_bullet_1,
        "{{PROJ_1_BULLET_2}}": dados.proj_1_bullet_2,
        "{{PROJ_1_BULLET_3}}": dados.proj_1_bullet_3,
        "{{PROJ_2_TITULO}}": dados.proj_2_titulo,
        "{{PROJ_2_LINK}}": dados.proj_2_link,
        "{{PROJ_2_BULLET_1}}": dados.proj_2_bullet_1,
        "{{PROJ_2_BULLET_2}}": dados.proj_2_bullet_2,
        "{{PROJ_2_BULLET_3}}": dados.proj_2_bullet_3,
        "{{SKILLS_LINGUAGENS}}": dados.skills_linguagens,
        "{{SKILLS_FRAMEWORKS}}": dados.skills_frameworks,
        "{{SKILLS_BANCOS}}": dados.skills_bancos,
        "{{SKILLS_FERRAMENTAS}}": dados.skills_ferramentas,
    }

    requests = [
        {
            "replaceAllText": {
                "containsText": {"text": placeholder, "matchCase": True},
                "replaceText": valor,
            }
        }
        for placeholder, valor in substituicoes.items()
    ]

    # Passo C: Aplicar todas as substituições de uma vez no Google Docs
    docs_service.documents().batchUpdate(
        documentId=novo_doc_id, body={"requests": requests}
    ).execute()

    return f"https://docs.google.com/document/d/{novo_doc_id}/edit"

# Execução interativa no Terminal
def ler_vaga_terminal() -> str:
    print("Cole a descrição da vaga abaixo.")
    print("Quando terminar, digite FIM em uma nova linha e pressione Enter:\n")
    linhas = []
    while True:
        linha = input()
        if linha.strip().upper() == "FIM":
            break
        linhas.append(linha)
    return "\n".join(linhas)


if __name__ == "__main__":
    descricao_vaga = ler_vaga_terminal()

    if not descricao_vaga.strip():
        print("Nenhuma descrição informada. Encerrando.")
        exit(0)

    print("\nAnalisando vaga e gerando adaptação...")
    resultado = agente.run_sync(f"Adapte meu currículo para esta vaga:\n{descricao_vaga}")

    # Exibe qual modelo da cadeia Fallback respondeu
    modelo_usado = resultado.response.model_name
    print(f"-> [LLM] Modelo utilizado: {modelo_usado}")

    dados = resultado.output
    print(f"-> [Docs] Gerando arquivo '{dados.nome_arquivo}' no Google Docs...")
    link_curriculo = gerar_curriculo_no_docs(dados)

    print("\n=== CURRÍCULO GERADO COM SUCESSO ===")
    print(f"Link para revisar e baixar em PDF: {link_curriculo}")