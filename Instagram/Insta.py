import http.client
import json
import pandas as pd
from lib import search_users, get_user_info, df_user_posts, calcular_engagement

def final(
    query,
    max_results=20,
    min_followers=50000,
    min_engagement=0.03
):
    #Search Posts
        #Sacar usuarios - influencers
        #Falta añadir que de una query se busquen 20 diferentes relacionadas
    df = search_users(query)
    #User info
        #De cada usuario mirar si cumple los minimos
    df_total=[]
    for i in df["Username"]:
        df_user_i = get_user_info(i)
        if df_user_i["Followers"] > min_followers:
            df_total.concat(df_user_i)
    #User POsts
        #De los que si cumplen los minimos buscar las publicaciones de los ultimos 2 meses y guardar likes, comentarios...
        #Calcular engagement de cada video y hacer media 
        #Devolver los que superen el engagemtn minimo
    #Guardar lista en Excel
    return df


df = df_user_posts()
print(df.head())
e = calcular_engagement(df)
print(e)
