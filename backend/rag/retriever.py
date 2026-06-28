from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from backend.config import get_settings
from backend.rag.indexer import vectorstore

settings = get_settings()


def search_documents(query: str, k: int = 6) -> str:
    """
    Recherche les chunks les plus pertinents dans ChromaDB
    pour une question donnée.

    Args:
        query: La question en langage naturel
        k: Nombre de chunks à retourner (défaut: 4)

    Returns:
        Texte formaté avec les passages pertinents et leurs sources
    """

    # ─── Recherche par similarité ──────────────────────────
    # ChromaDB convertit la query en vecteur et cherche les k plus proches
    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return "Aucun document pertinent trouvé."

    # ─── Formatage des résultats ───────────────────────────
    # On inclut la source pour que l'agent puisse citer les documents
    output = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "Document inconnu")
        output.append(f"[Source {i} — {source}]\n{doc.page_content}")

    return "\n\n---\n\n".join(output)