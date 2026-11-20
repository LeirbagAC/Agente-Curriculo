import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .models import DadosCurriculo
from .settings import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SCOPES,
    LOCAL_TEMPLATE_PATH,
)


def obter_credenciais_google() -> Credentials:
    """Autentica via OAuth 2.0 do usuário e salva/renova o token.json localmente."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", GOOGLE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_FILE, GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def gerar_curriculo_no_docs(dados: DadosCurriculo) -> str:
    """Envia o template .docx local convertendo para Google Docs e preenche os placeholders."""
    creds = obter_credenciais_google()

    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    file_metadata = {
        "name": dados.nome_arquivo,
        "mimeType": "application/vnd.google-apps.document",
    }

    media = MediaFileUpload(
        LOCAL_TEMPLATE_PATH,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    novo_doc = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    novo_doc_id = novo_doc.get("id")

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

    docs_service.documents().batchUpdate(
        documentId=novo_doc_id, body={"requests": requests}
    ).execute()

    return f"https://docs.google.com/document/d/{novo_doc_id}/edit"
