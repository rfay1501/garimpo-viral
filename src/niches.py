"""
Configuração dos nichos do garimpador.

Cada nicho tem:
  - name: nome amigável
  - rpm_score: 0-100, quanto maior, melhor a monetização (CPM/RPM)
  - affiliate_score: 0-100, potencial de afiliado
  - scale_score: 0-100, facilidade de reaproveitar em shorts/cortes
  - queries: dicionário de idioma -> lista de queries de busca
"""

LANGUAGE_NAMES = {
    "en": "Inglês",
    "es": "Espanhol",
    "pt": "Português",
}

NICHES = {
    "financas": {
        "name": "Finanças Pessoais & Renda Extra",
        "rpm_score": 95,
        "affiliate_score": 95,
        "scale_score": 85,
        "queries": {
            "en": [
                "passive income ideas 2026",
                "how to make money online beginners",
                "credit score tips",
            ],
            "es": [
                "ingresos pasivos 2026",
                "como ganar dinero extra desde casa",
            ],
            "pt": [
                "renda passiva 2026",
                "como ganhar dinheiro extra em casa",
            ],
        },
    },
    "misterios": {
        "name": "Curiosidades Bizarras & Mistérios",
        "rpm_score": 55,
        "affiliate_score": 40,
        "scale_score": 95,
        "queries": {
            "en": [
                "unsolved mysteries that baffled scientists",
                "strange historical events",
                "bizarre facts nobody knows",
            ],
            "es": [
                "misterios sin resolver",
                "curiosidades historicas increibles",
            ],
            "pt": [
                "misterios sem explicacao",
                "curiosidades historicas bizarras",
            ],
        },
    },
    "saude": {
        "name": "Saúde & Longevidade",
        "rpm_score": 80,
        "affiliate_score": 85,
        "scale_score": 75,
        "queries": {
            "en": [
                "longevity habits proven science",
                "sleep optimization tips",
                "anti aging daily routine",
            ],
            "es": [
                "habitos para vivir mas",
                "como dormir mejor ciencia",
            ],
            "pt": [
                "habitos longevidade ciencia",
                "como dormir melhor naturalmente",
            ],
        },
    },
    "psicologia_social": {
        "name": "Relacionamentos & Psicologia Social",
        "rpm_score": 50,
        "affiliate_score": 55,
        "scale_score": 95,
        "queries": {
            "en": [
                "female body language signs attraction",
                "male psychology explained",
                "dark psychology tactics",
            ],
            "es": [
                "lenguaje corporal atraccion",
                "psicologia oscura tactics",
            ],
            "pt": [
                "linguagem corporal atracao",
                "psicologia feminina sinais",
            ],
        },
    },
    "motivacao_masculina": {
        "name": "Motivação Masculina & Disciplina",
        "rpm_score": 60,
        "affiliate_score": 70,
        "scale_score": 90,
        "queries": {
            "en": [
                "stoic morning routine discipline",
                "masculine mindset focus",
                "how to build iron discipline",
            ],
            "es": [
                "rutina estoica disciplina",
                "mentalidad masculina enfoque",
            ],
            "pt": [
                "rotina estoica disciplina",
                "mentalidade alfa foco",
            ],
        },
    },
    "luxo": {
        "name": "Luxo & Vida de Milionários",
        "rpm_score": 75,
        "affiliate_score": 60,
        "scale_score": 80,
        "queries": {
            "en": [
                "billionaire daily habits",
                "most expensive mansions",
                "how billionaires think",
            ],
            "es": [
                "habitos de billonarios",
                "mansiones mas caras del mundo",
            ],
            "pt": [
                "habitos dos bilionarios",
                "mansoes mais caras do mundo",
            ],
        },
    },
    "historia": {
        "name": "História Resumida",
        "rpm_score": 50,
        "affiliate_score": 35,
        "scale_score": 80,
        "queries": {
            "en": [
                "ancient empire rise and fall",
                "forgotten battles history",
                "dark medieval history",
            ],
            "es": [
                "imperios antiguos caida",
                "batallas historicas olvidadas",
            ],
            "pt": [
                "imperios antigos queda",
                "batalhas historicas esquecidas",
            ],
        },
    },
    "ia_tech": {
        "name": "IA & Tecnologia Prática",
        "rpm_score": 85,
        "affiliate_score": 95,
        "scale_score": 70,
        "queries": {
            "en": [
                "best ai tools 2026",
                "ai automation workflow",
                "chatgpt productivity hacks",
            ],
            "es": [
                "mejores herramientas ia 2026",
                "automatizacion con ia",
            ],
            "pt": [
                "melhores ferramentas ia 2026",
                "automacao com ia",
            ],
        },
    },
    "true_crime": {
        "name": "True Crime",
        "rpm_score": 55,
        "affiliate_score": 30,
        "scale_score": 85,
        "queries": {
            "en": [
                "unsolved murder cases documentary",
                "serial killer cold case",
                "creepy disappearance cases",
            ],
            "es": [
                "casos de asesinato sin resolver",
                "asesinos en serie documental",
            ],
            "pt": [
                "crimes reais sem solucao",
                "assassinos em serie documentario",
            ],
        },
    },
    "espiritualidade": {
        "name": "Espiritualidade & Filosofia",
        "rpm_score": 45,
        "affiliate_score": 50,
        "scale_score": 85,
        "queries": {
            "en": [
                "stoic philosophy life lessons",
                "ancient symbolism meaning",
                "jungian shadow work explained",
            ],
            "es": [
                "filosofia estoica lecciones",
                "simbolismo antiguo significado",
            ],
            "pt": [
                "filosofia estoica licoes",
                "simbolismo antigo significado",
            ],
        },
    },
}


def all_queries():
    """Yield (niche_key, lang, query) tuples for every configured query."""
    for niche_key, cfg in NICHES.items():
        for lang, queries in cfg["queries"].items():
            for q in queries:
                yield niche_key, lang, q
