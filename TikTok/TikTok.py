import http.client
import json
import pandas as pd
from lib import search_posts, get_user_info

def final(
    keyword,
    max_results=20,
    min_followers=50000,
    min_engagement=0.03
):
    #Search Posts
        #Sacar usuarios - influencers
    df_posts = search_posts(keyword)
    #User info
        #De cada usuario mirar si cumple los minimos
    df_users = []
    for user in df_posts["AutorID"].unique():
        df_user_i = get_user_info(user)
        followers = df_user_i.loc[0, "followerCount"]
        if followers > min_followers:
            continue
        df_users.concat(df_user_i)
    #User POsts
        #De los que si cumplen los minimos buscar las publicaciones de los ultimos 2 meses y guardar likes, comentarios...
        #Calcular engagement de cada video y hacer media 
        #Devolver los que superen el engagemtn minimo
    #get_user_posts_last_2_months -- Funcion que se encargue de dado un usuario buscar sus videos de los dos ultimos meses! Usaria User Posts
    #Guardar lista en Excel
    return

# df = search_posts("OnePiece")
# print(df.head())

df = get_user_info("katyperry")
print(df)
