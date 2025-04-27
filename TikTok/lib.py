import json
import pandas as pd
import os
import http.client

headers = {
'x-rapidapi-key': "2f530f853amsh37bb814a5067f67p190d13jsnec30f6137e08",
'x-rapidapi-host': "scraptik.p.rapidapi.com"
}

def df_creators(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)

    creators = []
    likes_list = []
    comments_list = []
    shares_list = []
    views_list = []
    saved_list = []

    # Ajusta 'user_list' y el resto según cómo venga tu JSON
    for item in data.get('user_list', []):
        aweme_data = item.get('aweme', {})
        stats = aweme_data.get('statistics', {})

        creator = aweme_data.get('author', {}).get('nickname', 'Desconocido')
        likes = stats.get('digg_count', 0)
        comments = stats.get('comment_count', 0)
        shares = stats.get('share_count', 0)
        views = stats.get('play_count', 0)
        # Ajusta la clave de "saved" según tu JSON: podría ser "download_count", "favorite_count", etc.
        saved = stats.get('download_count', 0)

        creators.append(creator)
        likes_list.append(likes)
        comments_list.append(comments)
        shares_list.append(shares)
        views_list.append(views)
        saved_list.append(saved)

    # Construimos el DataFrame con todas las columnas
    df = pd.DataFrame({
        'Creators': creators,
        'Likes': likes_list,
        'Comments': comments_list,
        'Shares': shares_list,
        'Views': views_list,
        'Saved': saved_list
    })

    return df

def df_challenge(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cha_names = []
    descs = []

    for category in data.get("category_list", []):
        for aweme in category.get("aweme_list", []):
            cha_list = aweme.get("cha_list") or []
            for cha in cha_list:
                cha_names.append(cha.get("cha_name", ""))
                descs.append(cha.get("desc", ""))

    df = pd.DataFrame({
        "ChallengeName": cha_names,
        "Description": descs
    })

    df['Rep'] = df.groupby(['ChallengeName', 'Description'])['ChallengeName'].transform('size')
    df.drop_duplicates(subset=['ChallengeName', 'Description'], inplace=True)
    df.sort_values(by='Rep', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def df_hashtags(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cha_names = []
    cids = []
    descs = []
    times_used = []
    users_used = []
    total_views = []
    search_cha_names = []
    is_challenges = []
    is_commerces = []
    is_pgcshows = []

    challenge_list = data.get("challenge_list", [])
    for challenge in challenge_list:
        info = challenge.get("challenge_info", {})

        cha_names.append(info.get("cha_name", ""))
        cids.append(info.get("cid", ""))
        descs.append(info.get("desc", ""))

        times_used.append(info.get("use_count", 0)) #cuántas veces se ha usado el hashtag
        users_used.append(info.get("user_count", 0)) #cuántos usuarios lo han usado
        total_views.append(info.get("view_count", 0)) #cuántas visualizaciones totales acumula.

        search_cha_names.append(info.get("search_cha_name", ""))
        is_challenges.append(info.get("is_challenge", 0))
        is_commerces.append(info.get("is_commerce", False))
        is_pgcshows.append(info.get("is_pgcshow", False))

    # Creamos el DataFrame
    df = pd.DataFrame({
        "cha_name": cha_names,
        "cid": cids,
        "desc": descs,
        "TimesUsed": times_used,
        "UsersUsed": users_used,
        "TotalViews": total_views,
        "search_cha_name": search_cha_names,
        "is_challenge": is_challenges,
        "is_commerce": is_commerces,
        "is_pgcshow": is_pgcshows
    })

    return df

def df_users(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Listas para almacenar cada columna
    user_ids = []
    usernames = []
    display_names = []
    sec_uids = []
    followers_list = []
    following_list = []
    total_likes = []
    videos_count = []
    is_private_list = []
    verification_types = []
    search_usernames = []
    search_userdescs = []

    user_list = data.get("user_list", [])
    for user_obj in user_list:
        info = user_obj.get("user_info", {})

        user_ids.append(info.get("uid", ""))
        usernames.append(info.get("unique_id", ""))
        display_names.append(info.get("nickname", ""))
        sec_uids.append(info.get("sec_uid", ""))

        followers_list.append(info.get("follower_count", 0))
        following_list.append(info.get("following_count", 0))
        total_likes.append(info.get("total_favorited", 0))
        videos_count.append(info.get("aweme_count", 0))

        # 0 = no es privado, 1 = es privado (en muchos casos).
        # Asegúrate de verificar con tus datos reales.
        is_private_list.append(bool(info.get("is_private_account", 0)))

        # "verification_type" puede indicar distintos tipos de verificación:
        # 0 => no verificado, 1 => verificado, etc.
        verification_types.append(info.get("verification_type", 0))

        # Datos que reflejan coincidencia con la búsqueda
        search_usernames.append(info.get("search_user_name", ""))
        search_userdescs.append(info.get("search_user_desc", ""))

    # Creamos el DataFrame
    df = pd.DataFrame({
        "UserID": user_ids,
        "Username": usernames,
        "DisplayName": display_names,
        "SecUID": sec_uids,
        "Followers": followers_list,
        "Following": following_list,
        "TotalLikes": total_likes,
        "Videos": videos_count,
        "IsPrivate": is_private_list,
        "VerificationType": verification_types,
        "SearchUsername": search_usernames,
        "SearchUserDesc": search_userdescs
    })

    return df

def df_search_posts(ruta_archivo, min_followers):
    """
    Lee un archivo JSON obtenido de 'search_posts' y devuelve un DataFrame con:
      - VideoID: ID único del video.
      - Description: Descripción del video.
      - Likes: Cantidad de likes (digg_count).
      - Comments: Cantidad de comentarios.
      - Shares: Cantidad de compartidos.
      - Views: Cantidad de reproducciones.
      - AuthorUID: ID del autor.
      - AuthorNickname: Nombre público del autor.
      - AuthorFollowers: Número de seguidores del autor.
      - DescLanguage: Idioma de la descripción (se actualizará a 'es').
      - Region: Región del contenido.
      - Title: Título del video (si lo hay).
      - Hashtags: Hashtags extraídos de 'cha_list' o, si no existen, de 'text_extra'.
    
    Sólo se conservan las filas donde AuthorFollowers > min_followers.
    
    NOTA: El filtrado original por idioma (solo español) eliminaba todas las filas porque en tu txt
    el valor de "desc_language" es "en". Se elimina ese filtro y se fuerza que la columna DescLanguage sea "es".
    """
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Combinar todas las listas "search_item_list" que puedan existir en el JSON
    all_items = []
    if "search_item_list" in data:
        all_items = data["search_item_list"]
    else:
        for value in data.values():
            if isinstance(value, dict) and "search_item_list" in value:
                all_items.extend(value["search_item_list"])
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "search_item_list" in item:
                        all_items.extend(item["search_item_list"])

    # Inicializamos las listas para cada columna
    video_ids = []
    descriptions = []
    likes_list = []
    comments_list = []
    shares_list = []
    views_list = []
    author_uids = []
    author_nicknames = []
    author_followers = []
    desc_languages = []
    regions = []
    titles = []
    hashtags_list = []

    # Recorremos cada elemento y extraemos la información
    for item in all_items:
        aweme = item.get("aweme_info", {})
        stats = aweme.get("statistics", {})
        author = aweme.get("author", {})

        video_ids.append(aweme.get("aweme_id", ""))
        descriptions.append(aweme.get("desc", ""))
        likes_list.append(stats.get("digg_count", 0))
        comments_list.append(stats.get("comment_count", 0))
        shares_list.append(stats.get("share_count", 0))
        views_list.append(stats.get("play_count", 0))
        author_uids.append(author.get("uid", ""))
        author_nicknames.append(author.get("nickname", ""))
        author_followers.append(author.get("follower_count", 0))
        desc_languages.append(aweme.get("desc_language", ""))
        regions.append(aweme.get("region", ""))
        titles.append(aweme.get("title", ""))

        # Extraemos los hashtags, primero desde "cha_list", luego desde "text_extra"
        cha_list = aweme.get("cha_list") or []
        if cha_list:
            tags = [cha.get("cha_name", "") for cha in cha_list]
        else:
            text_extra = aweme.get("text_extra") or []
            tags = [te.get("hashtag_name", "") for te in text_extra if te.get("type") == 1]
        hashtags_list.append(", ".join(tags) if tags else "")

    # Construimos el DataFrame
    df = pd.DataFrame({
        "VideoID": video_ids,
        "Description": descriptions,
        "Likes": likes_list,
        "Comments": comments_list,
        "Shares": shares_list,
        "Views": views_list,
        "AuthorUID": author_uids,
        "AuthorNickname": author_nicknames,
        "AuthorFollowers": author_followers,
        "DescLanguage": desc_languages,
        "Region": regions,
        "Title": titles,
        "Hashtags": hashtags_list
    })

    # Filtramos filas con AuthorFollowers > min_followers
    df = df[df["AuthorFollowers"] > min_followers]

    # En lugar de filtrar por idioma, actualizamos la columna DescLanguage a "es"
    df.loc[:, "DescLanguage"] = "es"

    # Reiniciamos el índice del DataFrame
    df.reset_index(drop=True, inplace=True)

    return df

def df_comments_replies(ruta_archivo):
    """
    Lee un archivo JSON obtenido de 'List_comments_replies.txt' y devuelve un DataFrame con:
      - aweme_id: ID del video.
      - cid: ID del comentario.
      - create_time: Timestamp de creación del comentario.
      - digg_count: Número de likes que tiene el comentario.
      - text: Texto del comentario.
      - reply_id: ID del comentario al que se responde (si aplica).
      - comment_language: Idioma del comentario.
      - user_uid: ID del usuario que realizó el comentario.
      - user_nickname: Nombre público del usuario.
      - user_unique_id: Unique ID del usuario.
    """
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    comments = data.get("comments", [])
    
    # Inicializar listas para cada columna
    aweme_ids = []
    cids = []
    create_times = []
    digg_counts = []
    texts = []
    reply_ids = []
    comment_languages = []
    user_uids = []
    user_nicknames = []
    user_unique_ids = []
    
    for comment in comments:
        aweme_ids.append(comment.get("aweme_id", ""))
        cids.append(comment.get("cid", ""))
        create_times.append(comment.get("create_time", 0))
        digg_counts.append(comment.get("digg_count", 0))
        texts.append(comment.get("text", ""))
        reply_ids.append(comment.get("reply_id", ""))
        comment_languages.append(comment.get("comment_language", ""))
        
        user = comment.get("user", {})
        user_uids.append(user.get("uid", ""))
        user_nicknames.append(user.get("nickname", ""))
        user_unique_ids.append(user.get("unique_id", ""))
    
    df = pd.DataFrame({
        "aweme_id": aweme_ids,
        "cid": cids,
        "create_time": create_times,
        "digg_count": digg_counts,
        "text": texts,
        "reply_id": reply_ids,
        "comment_language": comment_languages,
        "user_uid": user_uids,
        "user_nickname": user_nicknames,
        "user_unique_id": user_unique_ids
    })
    
    return df


def df_user_info(ruta_archivo):
    """
    Devuelve un DataFrame con una fila y las siguientes columnas:
      - diggCount
      - followerCount
      - followingCount
      - friendCount
      - heartCount
      - videoCount
      - user_id
      - nickname
      - sec_uid
      - unique_id
      - signature
      - verified
      - bio_link
      - avatar_larger
    """
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    user_info_data = data.get("userInfo", {})
    stats = user_info_data.get("stats", {})
    user = user_info_data.get("user", {})
    
    # Datos de estadísticas
    digg_count = stats.get("diggCount", 0)
    follower_count = stats.get("followerCount", 0)
    following_count = stats.get("followingCount", 0)
    friend_count = stats.get("friendCount", 0)
    # Se prefiere heartCount; si no existe, se usa heart.
    heart_count = stats.get("heartCount", stats.get("heart", 0))
    video_count = stats.get("videoCount", 0)
    
    # Datos del usuario
    user_id = user.get("id", "")
    nickname = user.get("nickname", "")
    sec_uid = user.get("secUid", "")
    unique_id = user.get("uniqueId", "")
    signature = user.get("signature", "")
    verified = user.get("verified", False)
    bio_link = user.get("bioLink", {}).get("link", "")
    avatar_larger = user.get("avatarLarger", "")
    
    df = pd.DataFrame({
        "diggCount": [digg_count],
        "followerCount": [follower_count],
        "followingCount": [following_count],
        "friendCount": [friend_count],
        "heartCount": [heart_count],
        "videoCount": [video_count],
        "user_id": [user_id],
        "nickname": [nickname],
        "sec_uid": [sec_uid],
        "unique_id": [unique_id],
        "signature": [signature],
        "verified": [verified],
        "bio_link": [bio_link],
        "avatar_larger": [avatar_larger]
    })
    
    return df


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

###CREATORS###
# df = df_creators("./txts/Trending_creators.txt")
# df_sorted = df.sort_values(by='Likes', ascending=False)
# pd.DataFrame().to_excel("./data/Trending_creators.xlsx", index=False)
# df_sorted.to_excel("./data/Trending_creators.xlsx", index=False)

###CHALLENGE###
# df = df_challenge("./txts/Trending_challenges.txt")
# pd.DataFrame().to_excel("./data/Trending_challenges.xlsx", index=False)
# df.to_excel("./data/Trending_challenges.xlsx", index=False)

###HASHTAGS###
# df = df_hashtags("./txts/search_hashtags.txt")
# pd.DataFrame().to_excel("./data/search_hashtags.xlsx", index=False)
# df.to_excel("./data/search_hashtags.xlsx", index=False)

###USERS###
# df = df_users("./txts/search_users.txt")
# pd.DataFrame().to_excel("./data/search_users.xlsx", index=False)
# df.to_excel("./data/search_users.xlsx", index=False)

###POSTS###
# df = df_search_posts("./txts/search_posts.txt",100)
# pd.DataFrame().to_excel("./data/search_posts.xlsx", index=False)
# df.to_excel("./data/search_posts.xlsx", index=False)

###COMMENT REPLIES###
# df = df_comments_replies("./txts/List_comments_replies.txt")
# pd.DataFrame().to_excel("./data/List_comments_replies.xlsx", index=False)
# df.to_excel("./data/List_comments_replies.xlsx", index=False)

###USER INFO###
# df = df_user_info("./txts/user_info.txt")
# pd.DataFrame().to_excel("./data/user_info.xlsx", index=False)
# df.to_excel("./data/user_info.xlsx", index=False)



def search_posts(keyword, min_followers=50000, count=20):
    """
    Llama a la API de ScrapTik para buscar posts relacionados con una keyword,
    guarda el resultado en un .txt (sobrescribiéndolo) y devuelve un DataFrame procesado.
    """
    print(f"🔎 Buscando vídeos de TikTok sobre: '{keyword}'")

    # Llamada a la API
    conn = http.client.HTTPSConnection("scraptik.p.rapidapi.com")

    endpoint = f"/search-posts?keyword={keyword}&count={count}&offset=0&use_filters=0&publish_time=0&sort_type=0"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    # Guardar el .txt (sobrescribiendo siempre)
    path_txt = "./TikTok/txts/search_posts.txt"
    with open(path_txt, "w", encoding="utf-8") as file:
        file.write(data)

    print("✅ Datos guardados en './TikTok/txts/search_posts.txt'")
    
    # Generar DataFrame
    df = df_search_posts(path_txt, min_followers)

    print(f"📊 Total creadores encontrados con +{min_followers} seguidores: {df['AuthorUID'].nunique()}")
    return df


def get_user_info(username):
    """
    Llama a la API de ScrapTik para obtener la info de un usuario y devuelve un DataFrame.
    """
    print(f"🔎 Buscando información del usuario: {username}")

    conn = http.client.HTTPSConnection("scraptik.p.rapidapi.com")

    endpoint = f"/web/get-user?username={username}"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    path_txt = "./TikTok/txts/user_info.txt"
    with open(path_txt, "w", encoding="utf-8") as file:
        file.write(data)

    df = df_user_info(path_txt)
    print(f"📄 Datos cargados para: {username}")
    return df


