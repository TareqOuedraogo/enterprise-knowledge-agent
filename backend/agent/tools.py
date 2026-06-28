from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.db.connection import sync_engine
from backend.config import get_settings

settings = get_settings()


# ─── Outil 1 : SQL ────────────────────────────────────────
@tool
def query_database(question: str) -> str:
    """
    Interroge la base de données PostgreSQL en langage naturel.
    Utilise cet outil quand la question concerne :
    - des clients, projets, commandes, pièces, fournisseurs, employés
    - des statistiques, historiques, statuts, budgets
    - toute donnée structurée de l'entreprise

    Args:
        question: La question en langage naturel à transformer en SQL

    Returns:
        Les résultats de la requête formatés en texte
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage

    # 1. Demander au LLM de générer le SQL
    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0,  # Température 0 = déterministe, crucial pour le SQL
        api_key=settings.openai_api_key
    )

    # Schéma fourni au LLM pour qu'il génère du SQL correct
    schema_context = """
    Tables disponibles dans la base de données PostgreSQL :

    clients (id, nom, secteur, pays, contact_email, created_at)
    employes (id, nom, poste, departement, email)
    projets (id, nom, description, statut, date_debut, date_fin_prevue, budget, client_id, responsable_id)
        statut: 'en_cours' | 'termine' | 'suspendu'
    pieces (id, reference, designation, matiere, norme, prix_unitaire)
    fournisseurs (id, nom, pays, certification, contact_email)
    commandes (id, numero, statut, quantite, prix_total, date_commande, date_livraison_prevue, client_id, projet_id, piece_id, fournisseur_id)
        statut: 'en_attente' | 'en_production' | 'livree' | 'annulee'
    """

    messages = [
        SystemMessage(content=f"""Tu es un expert SQL PostgreSQL.
Génère UNIQUEMENT la requête SQL brute, sans explication, sans markdown, sans backticks.
La requête doit se terminer par un point-virgule.

{schema_context}
"""),
        HumanMessage(content=question)
    ]

    # 2. Générer la requête SQL
    sql_response = llm.invoke(messages)
    sql_query = sql_response.content.strip()

    print(f"🔍 SQL généré : {sql_query}")

    # 3. Exécuter la requête
    try:
        with Session(sync_engine) as session:
            result = session.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()

            if not rows:
                return "Aucun résultat trouvé pour cette requête."

            # Formater les résultats en texte lisible
            output = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                output.append(str(row_dict))

            return f"Résultats ({len(rows)} lignes) :\n" + "\n".join(output)

    except Exception as e:
        return f"Erreur lors de l'exécution SQL : {str(e)}"


# ─── Outil 2 : RAG ────────────────────────────────────────
@tool
def search_documents(question: str) -> str:
    """
    Recherche dans les documents internes de l'entreprise.
    Utilise cet outil quand la question concerne :
    - des procédures qualité
    - des normes, plans, formulaires
    - des documents RH ou techniques
    - la validation de pièces, AS9100, soumissions client

    Args:
        question: La question à rechercher dans les documents

    Returns:
        Les passages pertinents trouvés dans les documents
    """
    from backend.rag.retriever import search_documents as rag_search
    return rag_search(question)

# ─── Outil 3 : Email (Partie 3 — placeholder) ─────────────
# ─── Outil 3 : Email ──────────────────────────────────────
@tool
def draft_email(instruction: str) -> str:
    """
    Génère un brouillon d'email professionnel.
    Utilise cet outil quand l'utilisateur veut :
    - rédiger un email
    - informer une équipe
    - préparer une communication
    - envoyer un résumé à quelqu'un

    Args:
        instruction: La description de l'email à rédiger

    Returns:
        Le brouillon d'email formaté prêt à envoyer
    """
    from backend.email.generator import generate_email, format_email_response
    email_data = generate_email(instruction)
    return format_email_response(email_data)


# ─── Liste des outils exposés à l'agent ───────────────────
# LangGraph utilisera cette liste pour le tool calling
TOOLS = [query_database, search_documents, draft_email]