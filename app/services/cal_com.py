import requests
from typing import Optional, List, Dict, Any
from config import settings


class CalComService:
    """Servicio para interactuar con la API de Cal.com"""

    def __init__(self):
        self.base_url = settings.calcom_url
        self.api_key = settings.calcom_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "cal-api-version": "2024-08-13",
        }

    def get_event_types(self) -> List[Dict]:
        """Obtiene los tipos de eventos disponibles"""
        url = f"{self.base_url}/api/v2/event-types"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("eventTypes", [])
        except Exception as e:
            print(f"Error getting event types: {e}")
            return []

    def get_event_type_by_slug(self, slug: str) -> Optional[Dict]:
        """Obtiene un tipo de evento por su slug"""
        url = f"{self.base_url}/api/v2/event-types"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            for event in data.get("eventTypes", []):
                if event.get("slug") == slug:
                    return event
            return None
        except Exception as e:
            print(f"Error getting event type: {e}")
            return None

    def get_availability(
        self, event_type_id: int, start_date: str, end_date: str
    ) -> List[Dict]:
        """Obtiene disponibilidad para un tipo de evento"""
        url = f"{self.base_url}/api/v2/schedules"
        # Por ahora retornamos slots genéricos
        # La integración real requiere obtener el schedule del profesional
        return []

    def create_booking(
        self,
        event_type_id: int,
        start: str,
        attendee_name: str,
        attendee_email: str,
        notes: str = "",
    ) -> Optional[Dict]:
        """Crea una reserva en Cal.com"""
        url = f"{self.base_url}/api/v2/bookings"
        payload = {
            "eventTypeId": event_type_id,
            "start": start,
            "attendees": [{"email": attendee_email, "name": attendee_name}],
            "location": {"type": "inPerson"} if notes else {},
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating booking: {e}")
            return None

    def get_bookings(self, status: str = "upcoming") -> List[Dict]:
        """Obtiene las reservas"""
        url = f"{self.base_url}/api/v2/bookings?status={status}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("bookings", [])
        except Exception as e:
            print(f"Error getting bookings: {e}")
            return []

    def cancel_booking(self, booking_id: int, reason: str = "") -> bool:
        """Cancela una reserva"""
        url = f"{self.base_url}/api/v2/bookings/{booking_id}/cancellation"
        payload = {"reason": reason}
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error cancelling booking: {e}")
            return False


calcom_service = CalComService()
