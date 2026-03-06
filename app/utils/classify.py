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


def get_treatment_details(category: str) -> dict:
    """Devuelve la duración en minutos y el ID/Nombre del doctor según la categoría, como se solicita en el requerimiento."""
    details = {
        "ortodoncia": {"duration": 30, "doctor_name": "Dra. Murad"},
        "conductos": {"duration": 60, "doctor_name": "Dra. Murad"},
        "extracciones": {"duration": 30, "doctor_name": "Dr. Silvestro"},
        "implantes": {"duration": 30, "doctor_name": "Dr. Silvestro"}, # Asumimos 30m por defecto, se puede ajustar
        "protesis": {"duration": 30, "doctor_name": "Dr. Silvestro"},
        "limpieza": {"duration": 15, "doctor_name": "Dr. Silvestro"}, # Asignado a Silvestro por defecto si no se especifica
        "consulta": {"duration": 15, "doctor_name": "Cualquiera"},
    }
    return details.get(category, {"duration": 15, "doctor_name": "Cualquiera"})
