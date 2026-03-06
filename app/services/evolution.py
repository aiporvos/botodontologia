import httpx
from typing import Optional
from config import settings


class EvolutionService:
    """Servicio para interactuar con Evolution API (WhatsApp) de forma asíncrona"""

    def __init__(self):
        self.base_url = settings.evolution_url
        self.api_key = settings.evolution_api_key
        self.instance_name = settings.evolution_instance_name
        self.instance_token = settings.evolution_instance_token
        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}

    async def _post(self, endpoint: str, payload: dict, params: dict = None) -> bool:
        """Helper para peticiones POST asíncronas"""
        url = f"{self.base_url}/{endpoint}/{self.instance_name}"
        if params is None:
            params = {}
        params["instanceToken"] = self.instance_token

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, headers=self.headers, json=payload, params=params
                )
                return response.status_code in [200, 201]
            except Exception as e:
                print(f"Error en Evolution API ({endpoint}): {e}")
                return False

    async def send_text(self, number: str, text: str) -> bool:
        """Envía un mensaje de texto por WhatsApp"""
        if "@c.us" not in number:
            number = f"{number}@c.us"

        payload = {"number": number, "textMessage": {"text": text}}
        return await self._post("message/sendText", payload)

    async def send_buttons(
        self,
        number: str,
        text: str,
        buttons: list,
        title: str = "Selecciona una opción",
    ) -> bool:
        """Envía mensaje con botones interactivos"""
        if "@c.us" not in number:
            number = f"{number}@c.us"

        formatted_buttons = []
        for i, btn in enumerate(buttons):
            formatted_buttons.append(
                {"buttonId": f"btn_{i}", "buttonText": {"displayText": btn}, "type": 1}
            )

        payload = {
            "number": number,
            "title": title,
            "textMessage": {"text": text},
            "buttons": formatted_buttons,
        }
        return await self._post("message/sendButtons", payload)

    async def send_list(
        self, number: str, text: str, sections: list, title: str = "Selecciona"
    ) -> bool:
        """Envía mensaje con lista interactiva"""
        if "@c.us" not in number:
            number = f"{number}@c.us"

        formatted_sections = []
        for section in sections:
            formatted_sections.append(
                {
                    "title": section.get("title", ""),
                    "rows": [
                        {"id": row.get("id", ""), "title": row.get("title", "")}
                        for row in section.get("rows", [])
                    ],
                }
            )

        payload = {
            "number": number,
            "title": title,
            "textMessage": {"text": text},
            "sections": formatted_sections,
        }
        return await self._post("message/sendList", payload)


evolution_service = EvolutionService()
