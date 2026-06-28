from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    État partagé qui circule entre tous les nœuds du graph LangGraph.
    Chaque nœud lit depuis cet état et peut y écrire.
    
    C'est la mémoire de travail de l'agent pour une requête donnée.
    """

    # ─── Entrée utilisateur ───────────────────────────────
    # La question posée par l'employé DCM
    user_input: str

    # ─── Historique des messages ──────────────────────────
    # Annotated + add_messages = LangGraph accumule les messages
    # au lieu de les écraser à chaque nœud
    messages: Annotated[list, add_messages]

    # ─── Résultats intermédiaires ─────────────────────────
    # Rempli par le nœud SQL si la question nécessite la base de données
    sql_result: str | None

    # Rempli par le nœud RAG si la question nécessite les documents
    rag_result: str | None

    # Rempli par le nœud Outlook si la question nécessite les emails
    email_result: str | None

    # ─── Routing ──────────────────────────────────────────
    # Liste des outils que l'agent a décidé d'utiliser
    # ex: ["sql"], ["rag"], ["sql", "rag", "email"]
    tools_used: list[str]

    # ─── Réponse finale ───────────────────────────────────
    # Produite par le nœud de synthèse après orchestration
    final_response: str | None