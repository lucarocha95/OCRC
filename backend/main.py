
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

origins = [
    "https://lucarocha95.github.io",
    "https://www.lucarocha95.github.io",
    "http://127.0.0.1:5500",  # Live Server do VS Code
    "http://localhost:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = "https://tvxsgovslvvflzltutkb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2eHNnb3ZzbHZ2Zmx6bHR1dGtiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg2MTEyMTgsImV4cCI6MjA2NDE4NzIxOH0.aeZJtAGHHeskjz90UjuRPai5ld1ZI1EaxZWrNiaZabg"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

class Rating(BaseModel):
    bathroom_id: str
    user_id: str
    comments: str
    nota_limpeza: int
    nota_disponibilidade: int
    nota_atendimento: int
    nota_proximidade_pista: int
    nota_preco: int

@app.get("/bathrooms")
def listar_banheiros():
    res = requests.get(f"{SUPABASE_URL}/rest/v1/bathrooms?select=*", headers=HEADERS)
    return res.json()

@app.get("/bathrooms/{bathroom_id}")
def detalhes_banheiro(bathroom_id: str):
    b_res = requests.get(f"{SUPABASE_URL}/rest/v1/bathrooms?bathroom_id=eq.{bathroom_id}", headers=HEADERS)
    if b_res.status_code != 200 or not b_res.json():
        raise HTTPException(status_code=404, detail="Banheiro não encontrado")

    a_res = requests.get(
        f"{SUPABASE_URL}/rest/v1/ratings?bathroom_id=eq.{bathroom_id}&order=timestamp.desc&limit=3",
        headers=HEADERS
    )

    avaliacoes = []
    if a_res.status_code == 200:
        for r in a_res.json():
            user_id = r.get("user_id")
            nome = "Anônimo"
            if user_id:

                u_res = requests.get(f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}", headers=HEADERS)

                if u_res.status_code == 200 and u_res.json():
                    nome = u_res.json()[0].get("nome", "Anônimo")

            avaliacoes.append({
                "nota_final": r.get("nota_final"),
                "comments": r.get("comments"),
                "autor": nome
            })

    return {
        "banheiro": b_res.json()[0],
        "avaliacoes": avaliacoes
    }

@app.post("/ratings")
def adicionar_rating(rating: Rating):
    nota_final = round((
        rating.nota_limpeza +
        rating.nota_disponibilidade +
        rating.nota_atendimento +
        rating.nota_proximidade_pista +
        rating.nota_preco
    ) / 5, 2)

    payload = {
        "bathroom_id": rating.bathroom_id,
        "user_id": rating.user_id,
        "comments": rating.comments,
        "nota_limpeza": rating.nota_limpeza,
        "nota_disponibilidade": rating.nota_disponibilidade,
        "nota_atendimento": rating.nota_atendimento,
        "nota_proximidade_pista": rating.nota_proximidade_pista,
        "nota_preco": rating.nota_preco,
        "nota_final": nota_final
    }
    
    res = requests.post(f"{SUPABASE_URL}/rest/v1/ratings", headers=HEADERS, json=payload)
    
    if res.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail="Erro ao salvar avaliação")

    # Atualizar média do banheiro
    media_res = requests.get(
        f"{SUPABASE_URL}/rest/v1/ratings?bathroom_id=eq.{rating.bathroom_id}&select=nota_final",
        headers=HEADERS
    )

    if media_res.status_code == 200:
        notas = [r["nota_final"] for r in media_res.json()]
        if notas:
            nova_media = round(sum(notas) / len(notas), 2)
            update = requests.patch(
                f"{SUPABASE_URL}/rest/v1/bathrooms?bathroom_id=eq.{rating.bathroom_id}",
                headers=HEADERS,
                json={"media_final": nova_media}
            )

    return {"mensagem": "Avaliação registrada com sucesso."}
