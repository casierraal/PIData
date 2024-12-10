from fastapi import FastAPI
from scripts.api import cantidad_filmaciones_mes, cantidad_filmaciones_dia, score_titulo, votos_titulo, get_actor, get_director, recomendacion

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API de Recomendación de Películas!"}

@app.get("/cantidad_filmaciones_mes/{mes}")
def endpoint_cantidad_filmaciones_mes(mes: str):
    return cantidad_filmaciones_mes(mes)

@app.get("/cantidad_filmaciones_dia/{dia}")
def endpoint_cantidad_filmaciones_dia(dia: str):
    return cantidad_filmaciones_dia(dia)

@app.get("/score_titulo/{titulo}")
def endpoint_score_titulo(titulo: str):
    return score_titulo(titulo)

@app.get("/votos_titulo/{titulo}")
def endpoint_votos_titulo(titulo: str):
    return votos_titulo(titulo)

@app.get("/get_actor/{nombre_actor}")
def endpoint_get_actor(nombre_actor: str):
    return get_actor(nombre_actor)

@app.get("/get_director/{nombre_director}")
def endpoint_get_director(nombre_director: str):
    return get_director(nombre_director)

@app.get("/recomendacion/{titulo}")
def endpoint_recomendacion(titulo: str):
    return recomendacion(titulo)
