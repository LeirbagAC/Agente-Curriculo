# Agente-Curriculo

Aplicação de terminal que adapta um currículo para uma vaga de estágio a partir da descrição informada pelo usuário. O agente consulta projetos públicos do GitHub marcados com o tópico `portfolio`, gera informações técnicas estruturadas com modelos de IA e cria uma cópia preenchida do currículo no Google Docs.

## Funcionalidades

- Leitura interativa da descrição da vaga, encerrada pela palavra `FIM`.
- Consulta aos repositórios públicos do GitHub que possuam o tópico `portfolio`, excluindo forks.
- Leitura dos primeiros 2.000 caracteres do README de cada projeto encontrado.
- Geração estruturada de cargo, resumo, dois projetos, links e competências.
- Cadeia de fallback entre modelos Gemini, Groq/OpenAI e Groq.
- Conversão do template DOCX em novo Google Document.
- Criação automática da pasta `Curriculos Gerados - Agente` no Google Drive.
- Substituição dos placeholders do template pelos dados gerados.
- Exibição do modelo utilizado e do link do documento criado.

## Tecnologias utilizadas

- Python 3.12
- Pydantic e Pydantic AI
- PyGithub
- python-dotenv
- Google Drive API e Google Docs API
- Google OAuth 2.0
- Google Auth Library
- Groq, OpenAI-compatible provider e modelos Google por meio do Pydantic AI

## Arquitetura do projeto

O projeto utiliza um pacote Python modular e mantém `agente.py` como ponto de entrada compatível:

- `agente.py`: inicializa o cliente GitHub e o agente, além de iniciar o fluxo pelo terminal.
- `agente_curriculo/cli.py`: controla a entrada da descrição da vaga e a execução principal.
- `agente_curriculo/agent.py`: configura o agente, o prompt, o output estruturado e os modelos de fallback.
- `agente_curriculo/models.py`: define o schema Pydantic dos dados do currículo.
- `agente_curriculo/github_tools.py`: autentica no GitHub e pesquisa repositórios elegíveis.
- `agente_curriculo/google_docs.py`: realiza autenticação OAuth, cria a pasta no Drive e gera o documento.
- `agente_curriculo/settings.py`: carrega variáveis de ambiente e constantes de configuração.

## Pré-requisitos

- Python 3.12
- Conta no GitHub
- Token pessoal do GitHub com acesso de leitura aos repositórios públicos
- Conta do Google com acesso ao Google Drive
- Credenciais OAuth configuradas para Google Drive API e Google Docs API
- Chaves de acesso aos provedores de IA configurados na cadeia de fallback
- Template `Agente-Curriculo_Genérico.docx` na raiz do projeto

Não há arquivo de dependências como `requirements.txt`, `pyproject.toml` ou lockfile no projeto. O ambiente virtual já utilizado pelo projeto contém essas bibliotecas:

- `pydantic-ai`
- `pydantic`
- `PyGithub`
- `python-dotenv`
- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth`

## Configuração e execução

1. Crie e ative um ambiente virtual:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

2. Instale as dependências utilizadas pelo projeto:

```bash
pip install pydantic-ai pydantic PyGithub python-dotenv google-api-python-client google-auth-oauthlib google-auth
```

3. Copie o arquivo de exemplo e informe os valores locais:

```bash
cp .env.example .env
```

4. Coloque o arquivo `oauth_credentials.json` na raiz do projeto.

5. Confirme que `Agente-Curriculo_Genérico.docx` está na raiz. É esse template que será convertido em Google Document.

6. Execute o aplicativo:

```bash
python agente.py
```

7. Cole a descrição da vaga em linhas consecutivas. Para finalizar, digite `FIM` em uma nova linha.

Na primeira execução com Google, o navegador será aberto para autorização OAuth. O token gerado será salvo em `token.json`; nas execuções seguintes, ele será renovado automaticamente quando necessário.

## Configuração de ambiente

Exemplo seguro de `.env`:

```dotenv
GITHUB_TOKEN=seu_token_do_github
GROQ_API_KEY=sua_chave_da_groq
GOOGLE_CREDENTIALS_FILE=oauth_credentials.json
GEMINI_API_KEY=sua_chave_do_provedor_google
```

| Variável | Uso no projeto |
|---|---|
| `GITHUB_TOKEN` | Autentica o PyGithub para consultar os repositórios públicos. |
| `GROQ_API_KEY` | É passada diretamente ao modelo OpenAI-compatible hospedado na Groq. |
| `GOOGLE_CREDENTIALS_FILE` | Caminho do arquivo JSON de credenciais OAuth do Google. |
| `GEMINI_API_KEY` | Incluída no arquivo de exemplo para os modelos Google da cadeia de fallback. O módulo Python não lê essa variável diretamente; a integração depende do provedor Pydantic AI reconhecer a credencial configurada. |

`TEMPLATE_DOC_ID` aparece no `.env.example`, mas não é utilizada pela implementação atual. A integração usa o arquivo DOCX local definido em `LOCAL_TEMPLATE_PATH`.

Os arquivos `.env`, `*.json` e o diretório `venv` estão no `.gitignore`. Não versione chaves, tokens, `oauth_credentials.json` ou `token.json`.

## Fluxo de autenticação

### GitHub

O projeto cria um cliente PyGithub com `GITHUB_TOKEN`. A ferramenta de projeto lista os repositórios públicos do usuário autenticado e considera apenas aqueles que:

- não sejam forks;
- possuam o tópico `portfolio`.

Se o README não puder ser obtido, o projeto registra `Sem README disponível.` sem interromper a execução.

### Google

A autenticação usa OAuth 2.0 com o escopo `https://www.googleapis.com/auth/drive.file`. O projeto:

1. carrega `token.json`, quando existente;
2. renova o token expirado com refresh token;
3. inicia o fluxo local no navegador quando não existe token válido;
4. salva o novo token em `token.json`.

O documento criado é colocado na pasta `Curriculos Gerados - Agente`. Caso a pasta já exista, ela é reutilizada.

## Modelos de IA

O modelo resiliente é configurado nesta ordem de fallback:

1. `google:gemini-3.8-flash`
2. `google:gemini-3.5-flash-lite`
3. `openai/gpt-oss-120b`, via Groq
4. `groq:qwen/qwen3.8-27b`

O agente utiliza timeout de 60 segundos e output tipado por `PromptedOutput(DadosCurriculo)`.

## Schema gerado

O agente produz:

- nome do arquivo;
- cargo alvo;
- resumo profissional;
- título e link do primeiro projeto;
- três bullets do primeiro projeto;
- título e link do segundo projeto;
- três bullets do segundo projeto;
- linguagens, frameworks, bancos e ferramentas.

Esses campos substituem os placeholders correspondentes no template DOCX após a conversão para Google Docs.