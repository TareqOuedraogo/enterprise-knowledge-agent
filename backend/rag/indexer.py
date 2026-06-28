import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from backend.config import get_settings

settings = get_settings()

# ─── Chemins ──────────────────────────────────────────────
# Dossier contenant les PDFs générés
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "pdfs")

# Dossier où ChromaDB va stocker les vecteurs
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")


def get_embeddings():
    """
    Retourne le modèle d'embeddings OpenAI.
    text-embedding-3-small : rapide, économique, suffisant pour la démo.
    """
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.openai_api_key
    )


def index_documents() -> Chroma:
    """
    Charge tous les PDFs, les découpe en chunks, génère les embeddings
    et les stocke dans ChromaDB.
    Appelé une seule fois au démarrage si la base vectorielle est vide.
    """

    embeddings = get_embeddings()

    # ─── Vérification ─────────────────────────────────────
    # Si ChromaDB existe déjà, on charge sans réindexer
    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        print(" ChromaDB déjà indexé — chargement depuis le disque.")
        return Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        )

    print("🔍 Indexation des documents PDF en cours...")

    # ─── Chargement des PDFs ──────────────────────────────
    all_docs = []
    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]

    for pdf_file in pdf_files:
        pdf_path = os.path.join(DOCS_DIR, pdf_file)
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        # Ajouter le nom du fichier comme métadonnée
        for doc in docs:
            doc.metadata["source"] = pdf_file

        all_docs.extend(docs)
        print(f"   Chargé : {pdf_file} ({len(docs)} pages)")

    # ─── Découpage en chunks ───────────────────────────────
    # chunk_size=500 : assez petit pour être précis
    # chunk_overlap=50 : chevauchement pour ne pas perdre le contexte entre chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(all_docs)
    print(f"  ✂️  {len(chunks)} chunks générés")

    # ─── Génération des embeddings et stockage ─────────────
    # ChromaDB génère un vecteur pour chaque chunk et le stocke sur disque
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    print(f" Indexation terminée — {len(chunks)} chunks stockés dans ChromaDB.")
    return vectorstore


# ─── Instance globale ─────────────────────────────────────
# Chargée une seule fois au démarrage du backend
vectorstore = index_documents()