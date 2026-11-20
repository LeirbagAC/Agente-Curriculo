from pydantic import BaseModel, Field


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
