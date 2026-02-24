def classify_reason(reason: str) -> str:
    """
    Clasifica el motivo de consulta en categorías
    """
    r = (reason or "").lower()

    rules = [
        (
            "ortodoncia",
            [
                "bracket",
                "ortodon",
                "frenillo",
                "alineador",
                "invisalign",
                "ortondon",
                "矫正",
            ],
        ),
        (
            "conductos",
            [
                "conducto",
                "endodon",
                "me duele",
                "dolor",
                "nervio",
                "pulp",
                "matar nervio",
            ],
        ),
        (
            "extracciones",
            ["extraccion", "extraer", "sacar", "muela", "cordal", "juicio", "extracc"],
        ),
        ("implantes", ["implante", "tornillo", "perno", "implan"]),
        (
            "protesis",
            ["protesis", "dentadura", "placa", "corona", "puente", "prótesis"],
        ),
        ("consulta", ["consulta", "control", "revision", "chequeo", "revisar"]),
    ]

    for cat, keys in rules:
        if any(k in r for k in keys):
            return cat

    return "consulta"


def get_category_emoji(category: str) -> str:
    """Retorna emoji según categoría"""
    emojis = {
        "ortodoncia": "🦷",
        "conductos": "🔴",
        "extracciones": "🔧",
        "implantes": "⚙️",
        "protesis": "🦋",
        "consulta": "💬",
    }
    return emojis.get(category, "📅")
