import os
import json
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import get_settings

settings = get_settings()

# ─── Dossier de stockage des brouillons ───────────────────
DRAFTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "drafts")
os.makedirs(DRAFTS_DIR, exist_ok=True)


def generate_email(instruction: str, context: str = "") -> dict:
    """
    Génère un brouillon d'email professionnel avec GPT-4.1.
    Sauvegarde le brouillon en JSON dans drafts/.

    Args:
        instruction: Ce que l'email doit contenir
        context: Contexte additionnel (résultats SQL, documents, etc.)

    Returns:
        Dictionnaire avec to, subject, body, saved_path
    """

    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0.4,
        api_key=settings.openai_api_key
    )

    system_prompt = """Tu es un assistant de rédaction professionnelle pour DCM,
une entreprise de fabrication aéronautique de précision.

Tu génères des emails professionnels en français.
Tu réponds UNIQUEMENT en JSON valide avec cette structure exacte :
{
    "to": "destinataire@exemple.com",
    "subject": "Objet de l'email",
    "body": "Corps de l'email complet et professionnel"
}

Règles :
- Ton professionnel et formel
- Corps structuré avec salutation, contenu, conclusion
- Signature : DCM — Service concerné
- Pas de markdown dans le body, juste du texte"""

    user_message = f"""Instruction : {instruction}"""

    if context:
        user_message += f"\n\nContexte disponible :\n{context}"

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ])

    # ─── Parser le JSON ────────────────────────────────────
    try:
        # Nettoyer les backticks si le LLM en ajoute
        content = response.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        email_data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback si le JSON est mal formé
        email_data = {
            "to": "equipe@dcm.com",
            "subject": "Communication interne DCM",
            "body": response.content
        }

    # ─── Sauvegarder le brouillon ─────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"draft_{timestamp}.json"
    filepath = os.path.join(DRAFTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(email_data, f, ensure_ascii=False, indent=2)

    email_data["saved_path"] = filename
    print(f"✅ Brouillon sauvegardé : {filename}")

    return email_data


def format_email_response(email_data: dict) -> str:
    """
    Formate le brouillon pour l'affichage dans l'interface.
    """
    return f"""📧 Brouillon d'email généré :

À : {email_data.get('to', '')}
Objet : {email_data.get('subject', '')}

{email_data.get('body', '')}

---
 Brouillon sauvegardé : {email_data.get('saved_path', '')}
💡 En production : ce brouillon serait créé dans Outlook via Microsoft Graph API."""