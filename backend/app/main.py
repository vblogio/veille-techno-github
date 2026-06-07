from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import VeilleRequest, VeilleResponse
from .veille_service import VeilleService
import os
from datetime import datetime

app = FastAPI()

# CORS (pour permettre les requêtes depuis le frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du service
veille_service = VeilleService(
    github_token=os.getenv("GITHUB_TOKEN"),
    mistral_api_key=os.getenv("MISTRAL_API_KEY")
)

# Endpoints
@app.post("/run-veille", response_model=VeilleResponse)
async def run_veille(request: VeilleRequest):
    try:
        result = veille_service.run_veille(
            requetes=request.requetes,
            jours=request.jours,
            max_repos=request.max_repos
        )
        # Sauvegarder le rapport dans output/
        os.makedirs("/app/output", exist_ok=True)
        date_heure = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fichier_html = f"/app/output/veille_{date_heure}.html"
        with open(fichier_html, "w", encoding="utf-8") as f:
            f.write(result["rapport_html"])
        result["file"] = f"veille_{date_heure}.html"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    try:
        output_dir = "/app/output"
        rapports = []
        for fichier in os.listdir(output_dir):
            if fichier.endswith(".html") and fichier.startswith("veille_"):
                date_heure = fichier.replace("veille_", "").replace(".html", "")
                date_affichage = date_heure.replace("-", "/").replace("_", " : ")
                with open(os.path.join(output_dir, fichier), "r", encoding="utf-8") as f:
                    content = f.read()
                    count = content.count("<tr>") - 1  # Approximation
                rapports.append({
                    "file": fichier,
                    "date": date_affichage,
                    "count": count
                })
        rapports.sort(key=lambda x: x["file"], reverse=True)
        return {"rapports": rapports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/queries")
async def update_queries(requetes: List[str]):
    # À implémenter : sauvegarder les requêtes par défaut dans un fichier ou une base
    with open("/app/output/default_queries.json", "w", encoding="utf-8") as f:
        json.dump({"requetes": requetes}, f, indent=2)
    return {"status": "success", "requetes": requetes}

    