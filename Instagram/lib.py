import json
import pandas as pd
import http.client
from datetime import datetime, timedelta, timezone

headers = {
    'x-rapidapi-key': "0dae339b96msh77da504237e48fap1b8ed6jsnb5dfc08908d7",
    'x-rapidapi-host': "instagram-looter2.p.rapidapi.com"
}


def df_search_users():
    """
    Lee un archivo .txt con resultados de 'Search Users by query' de la API Instagram Looter
    y devuelve un DataFrame con columnas relevantes.
    """
    ruta_archivo = "./Instagram//txts/search_users_instagram.txt"
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)

    usuarios = data.get("users", [])
    resultados = []

    for item in usuarios:
        user = item.get("user", {})
        resultados.append({
            "UserID": user.get("id", ""),
            "Username": user.get("username", ""),
            "FullName": user.get("full_name", ""),
            "Verified": user.get("is_verified", False)
        })

    df = pd.DataFrame(resultados)
    return df

def search_users(query):
    """
    Llama al endpoint Search Users de Instagram Looter con una query.
    Guarda el resultado en un txt y devuelve un DataFrame con los usuarios encontrados.
    """
    print(f"🔍 Buscando usuarios de Instagram que coincidan con: '{query}'")

    conn = http.client.HTTPSConnection("instagram-looter2.p.rapidapi.com")
    endpoint = f"/search?query={query}&select=users"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    path_txt = "./Instagram/txts/search_users.txt"
    with open(path_txt, "w", encoding="utf-8") as file:
        file.write(data)

    print(f"✅ Datos guardados en '{path_txt}'")

    df = df_search_users()
    print(f"📄 {len(df)} usuarios cargados.")
    return df


def df_user_info():
    """
    Procesa el .txt generado por la API /profile?username=... y devuelve un DataFrame
    con la información del usuario.
    """
    ruta_archivo = "./Instagram/txts/user_info.txt"
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame([{
        "UserID": data.get("id", ""),
        "Username": data.get("username", ""),
        "FullName": data.get("full_name", ""),
        "Verified": data.get("is_verified", False),
        "Followers": data.get("edge_followed_by", {}).get("count", 0),
        "Following": data.get("edge_follow", {}).get("count", 0),
        "Biography": data.get("biography", ""),
        "Category": data.get("category_name", ""),
        "IsBusiness": data.get("is_business_account", False),
        "IsProfessional": data.get("is_professional_account", False),
        "PostsCount": data.get("edge_owner_to_timeline_media", {}).get("count", 0)
    }])

    return df

def get_user_info(username):
    """
    Llama a la API de Instagram Looter para obtener la info de un usuario.
    Guarda el resultado en un .txt y devuelve un DataFrame con la info procesada.
    """
    print(f"🔎 Buscando información del usuario: {username}")

    conn = http.client.HTTPSConnection("instagram-looter2.p.rapidapi.com")

    endpoint = f"/profile?username={username}"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    path_txt = "./Instagram/txts/user_info.txt"
    with open(path_txt, "w", encoding="utf-8") as file:
        file.write(data)

    print(f"✅ Datos guardados en {path_txt}")

    df = df_user_info()
    print(f"📄 Info procesada para: {username}")
    return df



def df_user_posts():
    """
    Procesa el archivo user_posts.txt generado por la API /user-feeds.
    Devuelve un DataFrame con posts de los últimos 2 meses y sus métricas clave.
    """
    path = "./Instagram/txts/user_posts.txt"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    resultados = []

    # Calcular fecha límite: hace 60 días
    fecha_limite = datetime.utcnow() - timedelta(days=60)

    for post in items:
        timestamp = post.get("taken_at")
        if not timestamp:
            continue

        fecha_post = datetime.utcfromtimestamp(timestamp)
        if fecha_post < fecha_limite:
            continue  # Ignorar posts antiguos

        caption_data = post.get("caption", {})
        caption_text = caption_data.get("text", "") if caption_data else ""

        resultados.append({
            "PostID": post.get("id", ""),
            "Caption": caption_text,
            "Likes": post.get("like_count", 0),
            "Comments": post.get("comment_count", 0),
            "TakenAt": fecha_post,
            "MediaType": post.get("media_type", "")
        })

    df = pd.DataFrame(resultados)
    return df


def calcular_engagement(df_posts):
    """
    Calcula el engagement medio de un usuario en base a su DataFrame de publicaciones.
    Engagement por post = (likes + comments) / total_interacciones
    Devuelve el engagement promedio de los últimos 2 meses.
    """
    if df_posts.empty:
        return 0.0

    # Filtrar por fecha (últimos 2 meses)
    fecha_limite = datetime.now(timezone.utc) - timedelta(days=60)
    recientes = df_posts[df_posts["TakenAt"] >= fecha_limite]

    if recientes.empty:
        return 0.0

    # Calcular engagement por post
    recientes["Engagement"] = (recientes["Likes"] + recientes["Comments"]) / (
        recientes["Likes"] + recientes["Comments"] + 1
    )

    # Promedio general
    engagement_promedio = recientes["Engagement"].mean()
    return round(engagement_promedio, 4)
