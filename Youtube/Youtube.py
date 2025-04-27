from lib import buscar_influencers_por_nicho
import pandas as pd

#def buscar_influencers_por_nicho(nicho: str, GPT, max_resultados, min_subs, min_videos, min_engagent, desde_enero = False):

buscar_influencers_por_nicho("Novedades en IA generativa", False, 20, 10000, 20, 0.05, False)


# df = buscar_influencers_con_engagement(
#     tema="nutrición",
#     max_resultados=20,
#     min_suscriptores=250000,
#     min_videos=10,
#     min_engagement=0.03,
#     desde_enero_2024=False
# )

# df.to_excel("./Youtube/data/influencers_nutricion.xlsx", index=False) #36'5%