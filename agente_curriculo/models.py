from pydantic import BaseModel, Field

class DadosCurriculo(BaseModel):
    nome_arquivo: str = Field(
        description="Nome curto sem espaços especiais, ex: CV_Gabriel_Backend_Java"
    )
    cargo_alvo: str = Field(
        description="Título profissional alinhado à vaga, ex: Desenvolvedor Back-End | Java & Spring Boot"
    )
    resumo: str = Field(
        description=(
            "Parágrafo fluido de 3 frases (350 a 480 caracteres) sem Markdown ou colchetes:\n"
            "Frase 1: Curso (7º período de Sistemas de Informação) + atuação na startup Health-Connect conectada ao contexto da vaga.\n"
            "Frase 2: Domínio técnico aplicado aos requisitos da vaga citando entregas reais (sem agrupar tecnologias de projetos diferentes como se fossem uma coisa só).\n"
            "Frase 3: Objetivo de estágio na área da vaga + diferencial relevante (ex: Inglês C1 ou vivência em entregas rápidas de startup).\n"
            "Evite repetir preposições seguidas (ex: 'com experiência... com React')."
        )
    )

    proj_1_titulo: str = Field(
        description="Nome limpo do projeto SEM crases ou asteriscos, ex: Android Monitor (android-monitor)"
    )
    proj_1_link: str
    proj_1_bullet_1: str = Field(
        description="Bullet seguindo obrigatoriamente: Verbo de ação no passado + escopo/tecnologia + resultado técnico concreto (máx. 180 caracteres)."
    )
    proj_1_bullet_2: str = Field(
        description="Bullet seguindo obrigatoriamente: Verbo de ação no passado + escopo/tecnologia + resultado técnico concreto (máx. 180 caracteres)."
    )
    proj_1_bullet_3: str = Field(
        description="Bullet seguindo obrigatoriamente: Verbo de ação no passado + escopo/tecnologia + resultado técnico concreto (máx. 180 caracteres)."
    )

    proj_2_titulo: str = Field(
        description="Nome limpo do projeto SEM crases ou asteriscos, ex: Simulador de E-commerce (SpringEcom)"
    )
    proj_2_link: str
    proj_2_bullet_1: str = Field(
        description="Bullet seguindo obrigatoriamente: Verbo de ação no passado + escopo/tecnologia + resultado técnico concreto (máx. 180 caracteres)."
    )
    proj_2_bullet_2: str = Field(
        description="Bullet seguindo obrigatoriamente: Verbo de ação no passado + escopo/tecnologia + resultado técnico concreto (máx. 180 caracteres)."
    )
    proj_2_bullet_3: str = Field(
        description="Bullet seguindo obrigatoriamente: Verbo de ação no passado + escopo/tecnologia + resultado técnico concreto (máx. 180 caracteres)."
    )

    skills_linguagens: str
    skills_frameworks: str
    skills_bancos: str
    skills_ferramentas: str