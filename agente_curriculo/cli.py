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


def executar() -> None:
    from .agent import criar_agente
    from .github_tools import criar_cliente_github
    from .google_docs import gerar_curriculo_no_docs
    from .settings import GITHUB_TOKEN

    descricao_vaga = ler_vaga_terminal()

    if not descricao_vaga.strip():
        print("Nenhuma descrição informada. Encerrando.")
        raise SystemExit(0)

    gh = criar_cliente_github(GITHUB_TOKEN)
    agente = criar_agente(gh)

    print("\nAnalisando vaga e gerando adaptação...")
    resultado = agente.run_sync(f"Adapte meu currículo para esta vaga:\n{descricao_vaga}")

    modelo_usado = resultado.response.model_name
    print(f"-> [LLM] Modelo utilizado: {modelo_usado}")

    dados = resultado.output
    print(f"-> [Docs] Gerando arquivo '{dados.nome_arquivo}' no Google Docs...")
    link_curriculo = gerar_curriculo_no_docs(dados)

    print("\n=== CURRÍCULO GERADO COM SUCESSO ===")
    print(f"Link para revisar e baixar em PDF: {link_curriculo}")
