from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, text
from backend.config import get_settings

# Charge les variables du .env via pydantic-settings
settings = get_settings()

# ─── Async engine (FastAPI + LangGraph) ───────────────────
# Utilisé partout dans l'app — non-bloquant, compatible async/await
async_engine = create_async_engine(
    settings.database_url,      # postgresql+asyncpg://...
    echo=False,                 # True = affiche chaque requête SQL dans le terminal (utile en debug)
    pool_size=10,               # Nb de connexions maintenues ouvertes en permanence
    max_overflow=20,            # Connexions supplémentaires autorisées si le pool est plein
)

# Factory de sessions async — crée une nouvelle session à chaque requête
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,     # Permet d'accéder aux objets après commit sans erreur async
)

# ─── Sync engine (seed.py uniquement) ─────────────────────
# Le seed est un script one-shot — pas besoin d'async ici
sync_engine = create_engine(
    settings.database_url_sync,  # postgresql+psycopg2://...
    echo=False,
)


# ─── Dependency FastAPI ────────────────────────────────────
# Injectée dans chaque route via Depends(get_db)
# Gère automatiquement commit / rollback / fermeture de session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session           # FastAPI utilise la session ici
            await session.commit()  # Commit si tout s'est bien passé
        except Exception:
            await session.rollback() # Annule tout si erreur
            raise


# ─── Init DB ──────────────────────────────────────────────
# Appelé une fois au démarrage de l'app (dans main.py)
# 1. Active l'extension pgvector (pour embeddings futurs — Partie 2)
# 2. Crée toutes les tables définies dans models.py si elles n'existent pas
async def init_db():
    from backend.db.models import Base  # Import local pour éviter les imports circulaires

    async with async_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)