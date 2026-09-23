#!/usr/bin/env python3
"""
Seed script for Firestore weather-fashion catalog.

Initializes the weather_fashion_items collection with seed outfits and items
tailored to diverse weather conditions (rain, cold, mild, hot).
"""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-2a3bfd66e57c"
COLLECTION_NAME = "weather_fashion_items"

SEED_ITEMS = [
    {
        "id": "trench-coat-chuva",
        "name": "Trench Coat Impermeável com Capuz",
        "category": "outerwear",
        "weather_condition": "chuva",
        "min_temp_c": 8.0,
        "max_temp_c": 20.0,
        "material": "Gore-Tex com forro respirável",
        "style": "Elegante e Clássico",
        "description": "Perfeito para dias chuvosos e com vento. Mantém o corpo seco sem esquentar demais.",
    },
    {
        "id": "bota-chelsea-impermeavel",
        "name": "Bota Chelsea de Borracha Impermeável",
        "category": "footwear",
        "weather_condition": "chuva",
        "min_temp_c": 5.0,
        "max_temp_c": 22.0,
        "material": "Borracha vulcanizada antiderrapante",
        "style": "Urbano / Casual",
        "description": "Protege contra poças e lama com acabamento sofisticado que combina com calças jeans ou alfaiataria.",
    },
    {
        "id": "sobretudo-la-frio",
        "name": "Sobretudo de Lã Batida Italiana",
        "category": "outerwear",
        "weather_condition": "frio",
        "min_temp_c": -5.0,
        "max_temp_c": 12.0,
        "material": "80% Lã batida, 20% Poliamida",
        "style": "Elegante e Sofisticado",
        "description": "Ideal para dias frios e noites de inverno rigoroso. Proporciona isolamento térmico de alta performance.",
    },
    {
        "id": "sueter-trico-merino",
        "name": "Suéter de Gola Alta em Lã Merino",
        "category": "top",
        "weather_condition": "frio",
        "min_temp_c": 2.0,
        "max_temp_c": 15.0,
        "material": "100% Lã Merino ultrafina",
        "style": "Minimalista e Elegante",
        "description": "Toque macio, excelente retenção térmica e respirabilidade. Não pinica e cabe sob qualquer casaco.",
    },
    {
        "id": "jaqueta-corta-vento",
        "name": "Jaqueta Corta-Vento Esportiva",
        "category": "outerwear",
        "weather_condition": "vento",
        "min_temp_c": 12.0,
        "max_temp_c": 22.0,
        "material": "Nylon ripstop resistente à água",
        "style": "Esportivo / Streetwear",
        "description": "Leve, compacta e resistente a rajadas de vento e chuviscos rápidos.",
    },
    {
        "id": "camisa-linho-calor",
        "name": "Camisa de Manga Longa em Puro Linho",
        "category": "top",
        "weather_condition": "calor",
        "min_temp_c": 22.0,
        "max_temp_c": 38.0,
        "material": "100% Linho europeu pré-lavado",
        "style": "Casual Chic / Balneário",
        "description": "Extremamente fresca e arejada. Absorve o calor e garante elegância mesmo sob sol forte.",
    },
    {
        "id": "vestido-midi-algodao",
        "name": "Vestido Midi Fluido em Algodão Orgânico",
        "category": "full_outfit",
        "weather_condition": "calor",
        "min_temp_c": 24.0,
        "max_temp_c": 40.0,
        "material": "100% Algodão orgânico",
        "style": "Feminino e Descontraído",
        "description": "Corte solto e tecido leve para manter o conforto térmico em dias ensolarados e abafados.",
    },
    {
        "id": "bermuda-chino-linho",
        "name": "Bermuda Chino em Misto Linho e Algodão",
        "category": "bottom",
        "weather_condition": "calor",
        "min_temp_c": 23.0,
        "max_temp_c": 38.0,
        "material": "55% Linho, 45% Algodão",
        "style": "Casual Elegante",
        "description": "Confortável e fresca, ideal para passeios em clima tropical ou verão intenso.",
    },
    {
        "id": "jaqueta-jeans-ameno",
        "name": "Jaqueta Jeans Tradicional Estruturada",
        "category": "outerwear",
        "weather_condition": "ameno",
        "min_temp_c": 15.0,
        "max_temp_c": 23.0,
        "material": "Jeans 100% algodão 12oz",
        "style": "Casual Clássico",
        "description": "Versátil para a meia-estação. Protege da brisa fresca sem esquentar excessivamente.",
    },
    {
        "id": "cardiga-algodao-ameno",
        "name": "Cardigã Leve de Algodão Pima",
        "category": "top",
        "weather_condition": "ameno",
        "min_temp_c": 16.0,
        "max_temp_c": 24.0,
        "material": "100% Algodão Pima peruano",
        "style": "Smart Casual",
        "description": "Fácil de sobrepor em camisas ou camisetas para alternar entre ambientes fechados e clima ameno.",
    },
    {
        "id": "oculos-sol-uv400",
        "name": "Óculos de Sol Polarizados com Proteção UV400",
        "category": "accessories",
        "weather_condition": "calor",
        "min_temp_c": 18.0,
        "max_temp_c": 45.0,
        "material": "Acetato italiano com lentes de policarbonato",
        "style": "Moderno e Atemporal",
        "description": "Proteção essencial para os olhos contra radiação solar em dias abertos e ensolarados.",
    },
    {
        "id": "cachecol-cashmere-frio",
        "name": "Cachecol Texturizado de Cashmere",
        "category": "accessories",
        "weather_condition": "frio",
        "min_temp_c": -10.0,
        "max_temp_c": 12.0,
        "material": "100% Cashmere da Mongólia",
        "style": "Inverno Clássico",
        "description": "Proteção térmica aconchegante para pescoço e tórax em dias gelados.",
    },
]


def seed_database():
    print(f"Connecting to Firestore with project='{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    print(f"Seeding {len(SEED_ITEMS)} fashion items into collection '{COLLECTION_NAME}'...")
    batch = db.batch()
    for item in SEED_ITEMS:
        doc_ref = collection.document(item["id"])
        batch.set(doc_ref, item)

    batch.commit()
    print("Seed completed successfully!")


if __name__ == "__main__":
    seed_database()
