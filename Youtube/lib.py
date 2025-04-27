import os
import requests
from dotenv import load_dotenv
import pandas as pd
import requests
from datetime import datetime, timedelta
from gpt import GPT
import json

# Cargar la clave API desde .env
os.environ.pop("YOUTUBE_API", None)

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API")

# --- Función para buscar vídeos relacionados con un tema ---
def buscar_videos(q, max_results):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": q,
        "type": "video",
        "maxResults": max_results,
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# --- Función para obtener estadísticas de canales por su ID ---
def obtener_datos_canales(channel_ids):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics",
        "id": ",".join(channel_ids),
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# --- Obtener estadísticas y detalles de los vídeos ---
def obtener_datos_videos(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["items"]


def buscar_influencers(busqueda, max_resultados, min_suscriptores, min_videos):
    """
    Busca influencers que hablen sobre un tema y filtra por suscriptores y número de vídeos.
    Devuelve un DataFrame con los resultados.
    """
    try:
        print(f"\n🔍 Buscando canales sobre: '{busqueda}'\n")

        videos = buscar_videos(busqueda, max_resultados)
        channel_ids = list({item["snippet"]["channelId"] for item in videos["items"]})

        canales = obtener_datos_canales(channel_ids)

        resultados = []

        for canal in canales["items"]:
            stats = canal["statistics"]
            snippet = canal["snippet"]

            suscriptores = int(stats.get("subscriberCount", 0))
            cantidad_videos = int(stats.get("videoCount", 0))

            if suscriptores >= min_suscriptores and cantidad_videos >= min_videos:
                nombre = snippet['title']
                canal_id = canal['id']
                url = f"https://www.youtube.com/channel/{canal_id}"

                print(f"📺 Canal: {nombre}")
                print(f"🔗 URL: {url}")
                print(f"👥 Suscriptores: {suscriptores:,}")
                print(f"🎥 Videos: {cantidad_videos}")
                print("-" * 50)

                resultados.append({
                    "Canal": nombre,
                    "Suscriptores": suscriptores,
                    "Videos": cantidad_videos,
                    "URL": url
                })

        if not resultados:
            print("❌ No se encontraron canales que cumplan los criterios.")

        return pd.DataFrame(resultados)

    except Exception as e:
        print(f"⚠️ Error al ejecutar la función: {e}")
        return pd.DataFrame()


def calcular_engagement(channel_id, desde_enero_2024=False, min_videos_requeridos=5):
    """
    Calcula el engagement promedio de los vídeos de un canal.
    - Si `desde_enero_2024` es True → usa vídeos desde 01/01/2024
    - Si es False → usa vídeos desde hace 2 meses
    - Solo calcula si hay al menos `min_videos_requeridos` vídeos válidos
    Engagement = (likes + comentarios) / visualizaciones
    """
    try:
        # Elegir fecha de inicio según parámetro
        if desde_enero_2024:
            published_after = "2024-01-01T00:00:00Z"
        else:
            fecha_hace_dos_meses = datetime.utcnow() - timedelta(days=60)
            published_after = fecha_hace_dos_meses.strftime("%Y-%m-%dT00:00:00Z")

        url_search = "https://www.googleapis.com/youtube/v3/search"
        video_ids = []
        next_page_token = None

        while True:
            params = {
                "part": "snippet",
                "channelId": channel_id,
                "type": "video",
                "order": "date",
                "publishedAfter": published_after,
                "maxResults": 50,
                "pageToken": next_page_token,
                "key": API_KEY
            }

            response = requests.get(url_search, params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                video_ids.append(item["id"]["videoId"])

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        if not video_ids:
            return {
                "channel_id": channel_id,
                "num_videos": 0,
                "engagement_promedio": 0.0
            }

        # Paso 2: Obtener estadísticas de los vídeos
        url_videos = "https://www.googleapis.com/youtube/v3/videos"
        engagement_rates = []

        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            params = {
                "part": "statistics",
                "id": ",".join(batch_ids),
                "key": API_KEY
            }

            response = requests.get(url_videos, params=params)
            response.raise_for_status()
            data = response.json()

            for video in data["items"]:
                stats = video.get("statistics", {})
                views = int(stats.get("viewCount", 0))
                likes = int(stats.get("likeCount", 0))
                comments = int(stats.get("commentCount", 0))

                if views > 0:
                    engagement = (likes + comments) / views
                    engagement_rates.append(engagement)

        # Verificar si hay suficientes vídeos válidos
        if len(engagement_rates) < min_videos_requeridos:
            return {
                "channel_id": channel_id,
                "num_videos": len(engagement_rates),
                "engagement_promedio": 0.0
            }

        promedio = sum(engagement_rates) / len(engagement_rates)

        return {
            "channel_id": channel_id,
            "num_videos": len(engagement_rates),
            "engagement_promedio": round(promedio, 4)
        }

    except Exception as e:
        print(f"❌ Error en calcular_engagement: {e}")
        return {
            "channel_id": channel_id,
            "num_videos": 0,
            "engagement_promedio": 0.0
        }



def buscar_influencers_con_engagement(
    tema,
    max_resultados=20,
    min_suscriptores=10000,
    min_videos=10,
    min_engagement=0.02,
    desde_enero_2024=False
):
    """
    Busca influencers que hablen sobre un tema en YouTube.
    Filtra por suscriptores, número de vídeos y engagement.
    Si desde_enero_2024=True → calcula el engagement desde 01/01/2024.
    Si False → calcula el engagement de los últimos 2 meses.
    Devuelve un DataFrame con los canales que cumplen los criterios.
    """
    try:
        print(f"\n🔍 Buscando influencers sobre: '{tema}'")

        videos = buscar_videos(tema, max_resultados)
        channel_ids = list({item["snippet"]["channelId"] for item in videos["items"]})
        canales = obtener_datos_canales(channel_ids)

        resultados = []

        for canal in canales["items"]:
            stats = canal["statistics"]
            snippet = canal["snippet"]

            suscriptores = int(stats.get("subscriberCount", 0))
            cantidad_videos = int(stats.get("videoCount", 0))
            canal_id = canal["id"]

            if suscriptores >= min_suscriptores and cantidad_videos >= min_videos:
                engagement_info = calcular_engagement(canal_id, desde_enero_2024=desde_enero_2024,min_videos_requeridos=min_videos)
                engagement = engagement_info["engagement_promedio"]
                videos_analizados = engagement_info["num_videos"]

                if engagement >= min_engagement and videos_analizados > 0:
                    resultados.append({
                        "Canal": snippet["title"],
                        "Suscriptores": suscriptores,
                        "Videos totales": cantidad_videos,
                        "Videos analizados": videos_analizados,
                        "Engagement promedio": engagement,
                        "URL": f"https://www.youtube.com/channel/{canal_id}"
                    })

        df_resultado = pd.DataFrame(resultados)

        if df_resultado.empty:
            print("❌ No se encontraron influencers que cumplan todos los criterios.")
        else:
            print(f"✅ {len(df_resultado)} influencers encontrados que cumplen los criterios.")

        return df_resultado

    except Exception as e:
        print(f"⚠️ Error al ejecutar la función completa: {e}")
        return pd.DataFrame()

def obtener_lista_desde_gpt(nicho: str) -> list[str]:
    resultado_texto = GPT(nicho)
    try:
        lista = json.loads(resultado_texto)
        if isinstance(lista, list) and all(isinstance(item, str) for item in lista):
            return lista
        else:
            raise ValueError("La respuesta no es una lista válida de strings.")
    except json.JSONDecodeError as e:
        raise ValueError(f"No se pudo convertir el resultado en lista: {e}")
    

def buscar_influencers_por_nicho(nicho: str, GPT, max_resultados, min_subs, min_videos, min_engagent, desde_enero = False):
    if GPT:
        subtemas = obtener_lista_desde_gpt(nicho)
        print(f"\n🎯 Nicho principal: {nicho}")
        print("📌 Subtemas generados por GPT:", subtemas)
    else:
        subtemas = [nicho]
    df_total = pd.DataFrame()

    for i, subtema in enumerate(subtemas):
        print(f"\n🔄 ({i+1}/{len(subtemas)}) Buscando influencers sobre: {subtema}")
        df = buscar_influencers_con_engagement(
            tema=subtema,
            max_resultados=max_resultados,
            min_suscriptores=min_subs,
            min_videos=min_videos,
            min_engagement=min_engagent,
            desde_enero_2024=desde_enero
        )
        df_total = pd.concat([df_total, df], ignore_index=True)
        break

    # Quitar duplicados por URL del canal
    df_total.drop_duplicates(subset=["URL"], inplace=True)

    # Guardar
    filename = f"./Youtube/data/influencers_{nicho.replace(' ', '_').lower()}.xlsx"
    df_total.to_excel(filename, index=False)

    print(f"\n✅ Guardado final: {len(df_total)} influencers únicos en {filename}")
    return df_total