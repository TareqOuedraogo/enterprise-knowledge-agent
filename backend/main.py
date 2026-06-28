from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.db.connection import init_db
from backend.db.seed import seed
from backend.api.routes import router

settings = get_settings()


# ─── Lifespan ─────────────────────────────────────────────
# Remplace l'ancien @app.on_event("startup") — pattern moderne FastAPI
# Tout ce qui est avant le `yield` s'exécute au démarrage
# Tout ce qui est après le `yield` s'exécute à l'arrêt
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Crée les tables PostgreSQL
    await init_db()

    # 2. Peuple la base avec les données de démo
    seed()

    # 3. Indexe les documents PDF dans ChromaDB
    from backend.rag.indexer import index_documents
    index_documents()

    print("🚀 Enterprise Knowledge Agent — démarré")
    yield
    print("🛑 Arrêt du serveur")

# ─── App ──────────────────────────────────────────────────
app = FastAPI(
    title="Enterprise Knowledge Agent",
    description="Agent IA multi-sources : SQL · RAG · Outlook",
    version="1.0.0",
    lifespan=lifespan,
)


# ─── CORS ─────────────────────────────────────────────────
# Permet au frontend React (port 3000) de parler au backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # En prod : domaine réel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ───────────────────────────────────────────────
# Préfixe /api/v1 — bonne pratique pour versionner l'API
app.include_router(router, prefix="/api/v1")


# ─── Health check racine ──────────────────────────────────
# Permet de vérifier rapidement que le serveur tourne
@app.get("/")
async def root():
    return {"status": "ok", "service": "Enterprise Knowledge Agent"}