# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import re
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


MODEL = "gemini-3.6-flash"


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback triggered after each agent turn to persist long-term memories."""
    if getattr(callback_context._invocation_context, "memory_service", None) is not None:
        await callback_context.add_session_to_memory()
    return None


def get_weather(query: str) -> str:
    """Gets real-time weather information for a given city or location.

    Args:
        query: A string containing the city or location to get weather information for (e.g. 'Nova York', 'São Paulo', 'San Francisco').

    Returns:
        A string with the real-time weather conditions for the queried location.
    """
    try:
        encoded_query = urllib.parse.quote(query.strip())
        url = f"https://wttr.in/{encoded_query}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            current = data["current_condition"][0]
            temp_c = current.get("temp_C", "")
            temp_f = current.get("temp_F", "")
            feels_like_c = current.get("FeelsLikeC", "")
            desc = current.get("weatherDesc", [{}])[0].get("value", "")
            humidity = current.get("humidity", "")
            wind = current.get("windspeedKmph", "")
            return (
                f"Condições climáticas atuais para {query}: "
                f"{desc}, {temp_c}°C ({temp_f}°F), sensação térmica de {feels_like_c}°C, "
                f"umidade relativa em {humidity}% e vento a {wind} km/h."
            )
    except Exception as e:
        return f"Não foi possível obter dados meteorológicos para {query}: {str(e)}"


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    city_lower = query.lower()
    tz_map = {
        "sf": "America/Los_Angeles",
        "san francisco": "America/Los_Angeles",
        "los angeles": "America/Los_Angeles",
        "nova york": "America/New_York",
        "new york": "America/New_York",
        "ny": "America/New_York",
        "sao paulo": "America/Sao_Paulo",
        "são paulo": "America/Sao_Paulo",
        "brasilia": "America/Sao_Paulo",
        "brasília": "America/Sao_Paulo",
        "londres": "Europe/London",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "toquio": "Asia/Tokyo",
        "tóquio": "Asia/Tokyo",
        "tokyo": "Asia/Tokyo",
    }
    tz_identifier = None
    for name, tz_val in tz_map.items():
        if name in city_lower:
            tz_identifier = tz_val
            break

    if not tz_identifier:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-2a3bfd66e57c"
FASHION_COLLECTION = "weather_fashion_items"
GCS_BUCKET_NAME = "weather-fashion-assets-2a3bfd66"
IMAGE_MODEL = "gemini-2.5-flash-image"


def get_fashion_recommendations(
    weather_condition: str | None = None,
    temperature_c: float | None = None,
    category: str | None = None,
) -> str:
    """Consults the Firestore fashion catalog to retrieve clothing and outfit recommendations based on weather conditions.

    Args:
        weather_condition: Optional condition like 'chuva', 'frio', 'calor', 'ameno', 'vento'.
        temperature_c: Optional ambient temperature in Celsius to filter suitable items (matching min_temp_c and max_temp_c).
        category: Optional clothing category to filter by (e.g. 'outerwear', 'top', 'bottom', 'footwear', 'accessories', 'full_outfit').

    Returns:
        A JSON string listing matching fashion items with descriptions, materials, and styles.
    """
    try:
        from google.cloud import firestore

        db = firestore.Client(project=FIRESTORE_PROJECT_ID)
        col = db.collection(FASHION_COLLECTION)
        docs = col.stream()

        matched_items = []
        for doc in docs:
            item = doc.to_dict()
            item["id"] = doc.id

            if category and item.get("category", "").lower() != category.strip().lower():
                continue

            if weather_condition and weather_condition.strip().lower() not in item.get("weather_condition", "").lower():
                continue

            if temperature_c is not None:
                min_t = item.get("min_temp_c", -100.0)
                max_t = item.get("max_temp_c", 100.0)
                if not (min_t <= temperature_c <= max_t):
                    continue

            matched_items.append(item)

        if not matched_items:
            return f"Nenhum item encontrado no catálogo para as condições especificadas (condição: {weather_condition}, temp: {temperature_c}°C, categoria: {category})."

        return json.dumps(matched_items, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Erro ao consultar o catálogo de moda no Firestore: {str(e)}"


def add_fashion_item(
    name: str,
    category: str,
    weather_condition: str,
    min_temp_c: float,
    max_temp_c: float,
    material: str = "",
    style: str = "",
    description: str = "",
) -> str:
    """Adds a new fashion item or outfit to the Firestore weather-fashion catalog.

    Args:
        name: Name of the garment or outfit (e.g. 'Casaco de Lã Teddy', 'Jaqueta de Couro').
        category: Category ('outerwear', 'top', 'bottom', 'footwear', 'accessories', 'full_outfit').
        weather_condition: Primary weather condition ('frio', 'chuva', 'calor', 'ameno', 'vento').
        min_temp_c: Minimum recommended temperature in Celsius.
        max_temp_c: Maximum recommended temperature in Celsius.
        material: Fabric or material description (e.g. '100% Algodão', 'Lã sintética', 'Couro legítimo').
        style: Style classification (e.g. 'Casual', 'Elegante', 'Streetwear').
        description: Advice on how and when to wear the item.

    Returns:
        A confirmation string with the registered item ID and details.
    """
    try:
        from google.cloud import firestore

        db = firestore.Client(project=FIRESTORE_PROJECT_ID)
        col = db.collection(FASHION_COLLECTION)

        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        doc_id = slug or f"item-{int(datetime.datetime.now().timestamp())}"

        item_data = {
            "id": doc_id,
            "name": name.strip(),
            "category": category.strip().lower(),
            "weather_condition": weather_condition.strip().lower(),
            "min_temp_c": float(min_temp_c),
            "max_temp_c": float(max_temp_c),
            "material": material.strip(),
            "style": style.strip(),
            "description": description.strip(),
        }

        col.document(doc_id).set(item_data)
        return f"Item '{name}' cadastrado com sucesso no catálogo Firestore (ID: {doc_id})."
    except Exception as e:
        return f"Erro ao adicionar item de moda no Firestore: {str(e)}"


def generate_and_save_outfit_image(prompt: str) -> str:
    """Generates an image of a fashion outfit/look using an AI image model and uploads it to the public Cloud Storage bucket.

    Args:
        prompt: Detailed visual description of the outfit/clothing to generate (e.g. 'A full-body photograph of a woman wearing a chic yellow trench coat, dark blue denim, and stylish waterproof boots on a rainy street').

    Returns:
        A message with the public URL of the uploaded image or an error description.
    """
    try:
        import uuid
        from google import genai
        from google.cloud import storage

        client = genai.Client(vertexai=True, project=FIRESTORE_PROJECT_ID, location="us-central1")
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
        )

        image_bytes = None
        for candidate in getattr(response, "candidates", []):
            content = getattr(candidate, "content", None)
            if content:
                for part in getattr(content, "parts", []):
                    inline_data = getattr(part, "inline_data", None)
                    if inline_data and getattr(inline_data, "data", None):
                        image_bytes = inline_data.data
                        break
            if image_bytes:
                break

        if not image_bytes:
            return "Não foi possível extrair a imagem gerada pelo modelo."

        filename = f"outfit_{uuid.uuid4().hex[:8]}.png"
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
        return f"Imagem do look gerada e salva com sucesso! URL pública: {public_url}"
    except Exception as e:
        return f"Erro ao gerar ou salvar imagem: {str(e)}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an intelligent, weather-aware fashion stylist assistant. "
        "You help users dress comfortably, stylishly, and appropriately for the weather in any location. "
        "When asked for outfit or clothing recommendations, first check the real-time weather using get_weather (if a city/location is mentioned). "
        "Then, use get_fashion_recommendations to search the Firestore catalog for suitable items based on the current weather condition and temperature. "
        "When requested by the user, you can also register new garments in the catalog using add_fashion_item. "
        "When the user asks to see, visualize, or generate an image of a look or outfit, use generate_and_save_outfit_image and share the resulting public image URL. "
        "You remember the user's stated preferences, style, and facts from previous conversations using your memory and use them to personalize your advice. "
        "Always respond in the language used by the user."
    ),
    tools=[
        get_weather,
        get_current_time,
        get_fashion_recommendations,
        add_fashion_item,
        generate_and_save_outfit_image,
        google_search,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
