from github import Github


def criar_cliente_github(token: str | None) -> Github:
    from github import Auth

    return Github(auth=Auth.Token(token))


def buscar_meus_projetos_github(gh: Github) -> str:
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
