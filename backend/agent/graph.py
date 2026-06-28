from langgraph.graph import StateGraph, END

from backend.agent.state import AgentState
from backend.agent.nodes import agent_node, tool_node, synthesis_node, should_use_tools


def build_graph():
    """
    Construit et compile le graph LangGraph de l'agent.

    Flux d'exécution :
    
    [START] → agent_node → should_use_tools ?
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
                "tools"               "synthesis"
                    │                       │
                tool_node             synthesis_node
                    │                       │
                    ▼                       ▼
            synthesis_node              [END]
                    │
                    ▼
                  [END]
    """

    # ─── Initialisation du graph ──────────────────────────
    # On passe AgentState comme schéma — LangGraph valide
    # chaque nœud contre ce TypedDict
    graph = StateGraph(AgentState)

    # ─── Ajout des nœuds ──────────────────────────────────
    # Chaque nœud a un nom unique et une fonction associée
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_node("synthesis", synthesis_node)

    # ─── Point d'entrée ───────────────────────────────────
    # Le graph commence toujours par agent_node
    graph.set_entry_point("agent")

    # ─── Routing conditionnel ─────────────────────────────
    # Après agent_node, should_use_tools() décide du chemin
    # "tools"     → le LLM veut appeler un outil
    # "synthesis" → le LLM répond directement sans outil
    graph.add_conditional_edges(
        "agent",
        should_use_tools,
        {
            "tools": "tools",
            "synthesis": "synthesis"
        }
    )

    # ─── Edges fixes ──────────────────────────────────────
    # Après l'exécution des outils → toujours synthèse
    graph.add_edge("tools", "synthesis")

    # Après la synthèse → toujours fin
    graph.add_edge("synthesis", END)

    # ─── Compilation ──────────────────────────────────────
    # compile() valide le graph et le prépare à l'exécution
    # Détecte les cycles infinis, les nœuds orphelins, etc.
    return graph.compile()


# ─── Instance globale du graph ────────────────────────────
# Importée par routes.py pour traiter les requêtes
enterprise_graph = build_graph()