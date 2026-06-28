from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from backend.agent.state import AgentState
from backend.agent.tools import TOOLS, query_database, search_documents, draft_email
from backend.config import get_settings

settings = get_settings()

# ─── LLM avec outils bindés ───────────────────────────────
# On attache les 3 outils au LLM — il peut maintenant décider de les appeler
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.3,  # Légèrement créatif pour les réponses finales
    api_key=settings.openai_api_key
)
llm_with_tools = llm.bind_tools(TOOLS)


# ─── Nœud 1 : Agent ───────────────────────────────────────
# Cerveau principal — reçoit la question et décide quoi faire
# Peut appeler un ou plusieurs outils, ou répondre directement
async def agent_node(state: AgentState) -> AgentState:
    """
    Nœud principal du graph.
    Reçoit l'état courant, envoie les messages au LLM,
    et retourne la décision du LLM (appel d'outil ou réponse finale).
    """

    system_prompt = """Tu es un assistant IA d'entreprise pour DCM, 
une entreprise spécialisée en fabrication aéronautique de précision.

Tu as accès aux outils suivants :
- query_database : pour interroger la base de données (clients, projets, commandes, pièces, fournisseurs)
- search_documents : pour rechercher dans les documents internes (procédures, normes, qualité)
- draft_email : pour rédiger des emails professionnels

Utilise les outils nécessaires pour répondre précisément.
Si la question nécessite plusieurs sources, utilise plusieurs outils.
Réponds toujours en français, de façon professionnelle et concise."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_input"])
    ]

    # Le LLM décide s'il appelle un outil ou répond directement
    response = await llm_with_tools.ainvoke(messages)

    return {
        **state,
        "messages": [response]  # add_messages accumule automatiquement
    }


# ─── Nœud 2 : Tools ───────────────────────────────────────
# Nœud préfabriqué LangGraph — exécute automatiquement les outils
# demandés par le LLM dans le nœud précédent
tool_node = ToolNode(TOOLS)


# ─── Nœud 3 : Synthèse ────────────────────────────────────
# Appelé après l'exécution des outils
# Agrège tous les résultats et produit la réponse finale
async def synthesis_node(state: AgentState) -> AgentState:
    """
    Reçoit les résultats des outils et demande au LLM
    de produire une réponse finale claire et structurée.
    """

    # Récupérer les résultats des outils depuis les messages
    tool_results = []
    tools_used = []

    for message in state["messages"]:
        # ToolMessage = résultat d'un outil exécuté
        if isinstance(message, ToolMessage):
            tool_results.append(f"Résultat ({message.name}) :\n{message.content}")
            tools_used.append(message.name)

    # Si aucun outil n'a été utilisé — réponse directe du LLM
    if not tool_results:
        last_message = state["messages"][-1]
        return {
            **state,
            "final_response": last_message.content,
            "tools_used": []
        }

    # Construire le contexte pour la synthèse
    context = "\n\n".join(tool_results)

    synthesis_prompt = f"""Tu es un assistant IA d'entreprise pour DCM.

Voici les données récupérées depuis les systèmes internes :

{context}

Question initiale : {state["user_input"]}

Synthétise ces informations en une réponse claire, structurée et professionnelle en français.
Si des données sont manquantes ou incomplètes, mentionne-le."""

    response = await llm.ainvoke([HumanMessage(content=synthesis_prompt)])

    return {
        **state,
        "final_response": response.content,
        "tools_used": tools_used
    }


# ─── Fonction de routing ──────────────────────────────────
# Appelée après agent_node pour décider du prochain nœud
# Retourne "tools" si le LLM veut appeler un outil
# Retourne "synthesis" si le LLM a répondu directement
def should_use_tools(state: AgentState) -> str:
    """
    Examine le dernier message du LLM.
    Si il contient des tool_calls → on exécute les outils.
    Sinon → on va directement à la synthèse.
    """
    last_message = state["messages"][-1]

    # LangChain met les appels d'outils dans tool_calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"  # → ToolNode

    return "synthesis"  # → synthesis_node