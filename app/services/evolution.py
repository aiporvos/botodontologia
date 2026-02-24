import requests
from typing import Optional
from config import settings


class EvolutionService:
    """Servicio para interactuar con Evolution API (WhatsApp)"""

    def __init__(self):
        self.base_url = settings.evolution_url
        self.api_key = settings.evolution_api_key
        self.instance_name = settings.evolution_instance_name
        self.instance_token = settings.evolution_instance_token
        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}

    def send_text(self, number: str, text: str) -> bool:
        """Envía un mensaje de texto por WhatsApp"""
        # Asegurar formato correcto del número
        if "@c.us" not in number:
            number = f"{number}@c.us"

        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        payload = {"number": number, "textMessage": {"text": text}}

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                params={"instanceToken": self.instance_token},
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False

    def send_buttons(
        self,
        number: str,
        text: str,
        buttons: list,
        title: str = "Selecciona una opción",
    ) -> bool:
        """Envía mensaje con botones interactivos"""
        if "@c.us" not in number:
            number = f"{number}@c.us"

        url = f"{self.base_url}/message/sendButtons/{self.instance_name}"

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

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                params={"instanceToken": self.instance_token},
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error sending buttons: {e}")
            return False

    def send_list(
        self, number: str, text: str, sections: list, title: str = "Selecciona"
    ) -> bool:
        """Envía mensaje con lista interactiva (más de 3 opciones)"""
        if "@c.us" not in number:
            number = f"{number}@c.us"

        url = f"{self.base_url}/message/sendList/{self.instance_name}"

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

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                params={"instanceToken": self.instance_token},
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error sending list: {e}")
            return False

    def get_qr_code(self) -> Optional[str]:
        """Obtiene el QR code para conectar WhatsApp"""
        url = f"{self.base_url}/instance/connect/{self.instance_name}"
        try:
            response = requests.get(
                url, headers=self.headers, params={"instanceToken": self.instance_token}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("qrcode", {}).get("code")
            return None
        except Exception as e:
            print(f"Error getting QR code: {e}")
            return None


evolution_service = EvolutionService()
