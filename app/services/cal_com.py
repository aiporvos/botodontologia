import httpx
from typing import Optional, List, Dict, Any
from config import settings
from datetime import datetime


class CalComService:
    """Servicio para interactuar con la API de Cal.com v2 de forma asíncrona"""

    def __init__(self):
        self.base_url = settings.calcom_url
        self.api_key = settings.calcom_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "cal-api-version": "2024-08-13",
        }

    async def get_event_types(self) -> List[Dict]:
        """Obtiene los tipos de eventos disponibles"""
        url = f"{self.base_url}/v2/event-types"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                # En v2 la estructura puede variar, ajustamos según documentación usual
                return data.get("data", {}).get("eventTypes", [])
            except Exception as e:
                print(f"Error getting event types: {e}")
                return []

    async def get_availability(
        self, event_type_id: int, start_date: str, end_date: str
    ) -> List[Dict]:
        """Obtiene disponibilidad real para un tipo de evento"""
        # API v2 endpoint para disponibilidad
        url = f"{self.base_url}/v2/slots/available"
        params = {
            "eventTypeId": event_type_id,
            "startTime": start_date,
            "endTime": end_date,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                # Retorna los slots disponibles
                slots_data = data.get("data", {}).get("slots", {})
                # Aplanamos los slots de todos los días en una lista simple
                all_slots = []
                for date_key, slots in slots_data.items():
                    all_slots.extend(slots)
                return all_slots
            except Exception as e:
                print(f"Error getting availability from Cal.com: {e}")
                return []

    async def create_booking(
        self,
        event_type_id: int,
        start: str,
        attendee_name: str,
        attendee_email: str,
        notes: str = "",
    ) -> Optional[Dict]:
        """Crea una reserva en Cal.com"""
        url = f"{self.base_url}/v2/bookings"
        payload = {
            "eventTypeId": event_type_id,
            "start": start,
            "attendees": [{"email": attendee_email, "name": attendee_name}],
            "location": {"type": "inPerson"} if notes else {},
            "notes": notes
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json().get("data")
            except Exception as e:
                print(f"Error creating booking in Cal.com: {e}")
                return None

    async def cancel_booking(self, booking_id: int, reason: str = "") -> bool:
        """Cancela una reserva"""
        url = f"{self.base_url}/v2/bookings/{booking_id}/cancel"
        payload = {"reason": reason}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                return response.status_code in [200, 201]
            except Exception as e:
                print(f"Error cancelling booking in Cal.com: {e}")
                return False


calcom_service = CalComService()
