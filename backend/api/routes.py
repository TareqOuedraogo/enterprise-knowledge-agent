from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.agent.graph import enterprise_graph
from backend.agent.state import AgentState

# ─── Router ───────────────────────────────────────────────
# Groupe tous les endpoints de l'agent sous /api/v1
router = APIRouter(prefix="/agent", tags=["agent"])


# ─── Schémas de requête / réponse ─────────────────────────
class ChatRequest(BaseModel):
    """Corps de la requête POST /chat"""
    message: str          # La question de l'employé DCM
    session_id: str = "default"  # Pour la mémoire future (Partie 2)


class ChatResponse(BaseModel):
    """Corps de la réponse"""
    response: str         # Réponse finale synthétisée
    tools_used: list[str] # Outils utilisés (sql, rag, email)
    session_id: str


# ─── Endpoints ────────────────────────────────────────────

@router.get("/health")
async def health():
    """
    Vérifie que l'agent est opérationnel.
    Utilisé par Docker et le frontend pour vérifier l'état du service.
    """
    return {"status": "ok", "agent": "enterprise-knowledge-agent"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Point d'entrée principal de l'agent.
    Reçoit la question de l'utilisateur, l'envoie au graph LangGraph,
    et retourne la réponse finale avec les outils utilisés.
    """
    try:
        # ─── Construire l'état initial ─────────────────────
        # On initialise AgentState avec la question de l'utilisateur
        # Tous les autres champs commencent à None ou []
        initial_state: AgentState = {
            "user_input": request.message,
            "messages": [],
            "sql_result": None,
            "rag_result": None,
            "email_result": None,
            "tools_used": [],
            "final_response": None
        }

        # ─── Invoquer le graph ─────────────────────────────
        # Le graph traverse tous les nœuds et retourne l'état final
        final_state = await enterprise_graph.ainvoke(initial_state)

        # ─── Extraire la réponse ───────────────────────────
        response_text = final_state.get("final_response")

        if not response_text:
            raise HTTPException(
                status_code=500,
                detail="L'agent n'a pas produit de réponse."
            )

        return ChatResponse(
            response=response_text,
            tools_used=final_state.get("tools_used", []),
            session_id=request.session_id
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur agent : {str(e)}"
        )