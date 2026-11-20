Agente-Curriculo
================

Gerador interativo de currículos adaptados a vagas de estágio.

Estrutura
---------

- `agente.py`: ponto de entrada compatível com a execução anterior.
- `agente_curriculo/settings.py`: variáveis de ambiente e constantes.
- `agente_curriculo/models.py`: schema estruturado da saída do agente.
- `agente_curriculo/github_tools.py`: autenticação e consulta dos repositórios.
- `agente_curriculo/agent.py`: configuração dos modelos, fallback e prompt.
- `agente_curriculo/google_docs.py`: autenticação OAuth e integração com Google Docs.
- `agente_curriculo/cli.py`: leitura da vaga e execução no terminal.

Execução
--------

```bash
venv/bin/python agente.py
```

Configure as credenciais conforme `.env.example` e mantenha `token.json`,
`oauth_credentials.json` e o template DOCX na raiz do projeto.