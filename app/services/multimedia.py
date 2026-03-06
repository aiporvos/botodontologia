import httpx
import base64
import os
from openai import AsyncOpenAI
from config import settings

class MultimediaService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def transcribe_audio(self, audio_base64: str) -> str:
        """Transcribe audio base64 usando OpenAI Whisper"""
        try:
            # Convertir base64 a archivo temporal
            audio_data = base64.b64decode(audio_base64)
            temp_filename = "/tmp/voice_msg.ogg"
            with open(temp_filename, "wb") as f:
                f.write(audio_data)

            with open(temp_filename, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    language="es"
                )
            
            os.remove(temp_filename)
            return transcript.text
        except Exception as e:
            print(f"Transcription Error: {e}")
            return "No pude entender el mensaje de voz."

    async def describe_image(self, image_base64: str) -> str:
        """Analiza una imagen usando GPT-4 Vision"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe brevemente qué se ve en esta imagen relacionada con salud bucal o consulta dental:"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Vision Error: {e}")
            return "No pude analizar la imagen."

multimedia_service = MultimediaService()
