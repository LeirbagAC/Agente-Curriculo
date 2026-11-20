import os

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")
TEMPLATE_DOC_ID = os.getenv("TEMPLATE_DOC_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
LOCAL_TEMPLATE_PATH = "Agente-Curriculo_Genérico.docx"
