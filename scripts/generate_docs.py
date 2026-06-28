from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
import os

# ─── Dossier de sortie ────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_styles():
    """Retourne les styles de mise en page."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CustomTitle",
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="CustomHeading",
        fontSize=13,
        spaceAfter=10,
        spaceBefore=15,
        fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="CustomBody",
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
        leading=14
    ))

    return styles


def create_procedure_validation_piece():
    """
    Document 1 : Procédure de validation d'une nouvelle pièce aéronautique.
    Simule un document qualité interne DCM.
    """
    path = os.path.join(OUTPUT_DIR, "procedure_validation_piece.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = get_styles()
    story = []

    story.append(Paragraph("DCM — Procédure de Validation d'une Nouvelle Pièce", styles["CustomTitle"]))
    story.append(Paragraph("Document QUA-001 | Version 3.2 | Juin 2024", styles["CustomBody"]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("1. Objet et domaine d'application", styles["CustomHeading"]))
    story.append(Paragraph(
        "Cette procédure définit les étapes obligatoires pour valider toute nouvelle pièce "
        "aéronautique fabriquée par DCM avant sa livraison au client. Elle s'applique à toutes "
        "les pièces structurelles, mécaniques et de précision produites dans nos ateliers, "
        "conformément aux exigences de la norme AS9100 révision D.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("2. Références normatives", styles["CustomHeading"]))
    story.append(Paragraph(
        "Les documents suivants sont indispensables pour l'application de cette procédure : "
        "AS9100 Rev D (Systèmes de management de la qualité pour l'aviation), "
        "NADCAP AC7004 (Procédés spéciaux aéronautiques), "
        "EN 9102 (First Article Inspection), "
        "MIL-STD-1916 (Contrôle qualité par échantillonnage).",
        styles["CustomBody"]
    ))

    story.append(Paragraph("3. Étapes de validation", styles["CustomHeading"]))
    story.append(Paragraph(
        "Étape 1 — Revue de conception : L'ingénieur responsable vérifie que les plans "
        "de fabrication correspondent aux spécifications client. Tout écart doit être documenté "
        "dans le formulaire ECR-001 et approuvé par le département qualité.",
        styles["CustomBody"]
    ))
    story.append(Paragraph(
        "Étape 2 — First Article Inspection (FAI) : La première pièce produite fait l'objet "
        "d'une inspection complète selon la norme EN 9102. Toutes les dimensions critiques "
        "sont mesurées et consignées dans le rapport FAI. Le taux d'acceptation minimum est "
        "de 98% pour les dimensions critiques.",
        styles["CustomBody"]
    ))
    story.append(Paragraph(
        "Étape 3 — Contrôle non destructif (CND) : Selon la criticité de la pièce, "
        "des contrôles par ultrasons, ressuage ou radiographie sont effectués. "
        "Les pièces de classe A (structurelles primaires) requièrent obligatoirement "
        "un contrôle par ultrasons certifié NADCAP.",
        styles["CustomBody"]
    ))
    story.append(Paragraph(
        "Étape 4 — Approbation finale : Le responsable qualité signe le certificat de conformité "
        "C of C avant toute expédition. Une copie est conservée dans le système ERP pendant "
        "10 ans minimum conformément aux exigences réglementaires.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("4. Responsabilités", styles["CustomHeading"]))
    story.append(Paragraph(
        "Ingénieur de production : Responsable des étapes 1 et 2. "
        "Technicien CND certifié : Responsable de l'étape 3. "
        "Responsable qualité : Approbation finale et signature du C of C. "
        "Direction : Revue annuelle de cette procédure.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("5. Enregistrements qualité", styles["CustomHeading"]))
    story.append(Paragraph(
        "Les enregistrements suivants doivent être complétés et archivés : "
        "Formulaire FAI-001 (First Article Inspection Report), "
        "Formulaire CND-002 (Rapport de contrôle non destructif), "
        "Certificat de conformité C of C signé, "
        "Rapport de mesures dimensionnelles.",
        styles["CustomBody"]
    ))

    doc.build(story)
    print(f"✅ Créé : {path}")


def create_norme_qualite_as9100():
    """
    Document 2 : Guide interne AS9100 DCM.
    Simule la documentation qualité de l'entreprise.
    """
    path = os.path.join(OUTPUT_DIR, "norme_qualite_as9100.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = get_styles()
    story = []

    story.append(Paragraph("DCM — Guide Qualité AS9100 Rev D", styles["CustomTitle"]))
    story.append(Paragraph("Document QUA-002 | Version 2.1 | Mars 2024", styles["CustomBody"]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("1. Présentation de la norme AS9100", styles["CustomHeading"]))
    story.append(Paragraph(
        "La norme AS9100 révision D est le standard international de management de la qualité "
        "pour l'industrie aéronautique, spatiale et de défense. DCM est certifié AS9100 Rev D "
        "depuis 2018. Cette certification est renouvelée tous les trois ans par un organisme "
        "accrédité et constitue un prérequis pour travailler avec Airbus, Bombardier et Bell.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("2. Exigences clés pour DCM", styles["CustomHeading"]))
    story.append(Paragraph(
        "Gestion des risques : DCM applique une analyse AMDEC (Analyse des Modes de Défaillance "
        "et de leurs Effets Critiques) sur tous les nouveaux projets. Cette analyse est réalisée "
        "en phase de conception et mise à jour à chaque modification significative.",
        styles["CustomBody"]
    ))
    story.append(Paragraph(
        "Traçabilité complète : Chaque pièce produite doit être traçable de la matière première "
        "jusqu'à la livraison finale. Les numéros de lot, certificats matière et rapports "
        "d'inspection sont conservés dans le système ERP pendant une durée minimale de 10 ans.",
        styles["CustomBody"]
    ))
    story.append(Paragraph(
        "Gestion des fournisseurs : Tous les fournisseurs de DCM doivent être approuvés "
        "et figurer sur la Liste des Fournisseurs Approuvés (LFA). Une évaluation annuelle "
        "est réalisée sur la base des critères de qualité, délai et coût.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("3. Processus d'audit interne", styles["CustomHeading"]))
    story.append(Paragraph(
        "DCM réalise des audits internes trimestriels pour vérifier la conformité aux exigences "
        "AS9100. Les non-conformités détectées font l'objet d'une action corrective documentée "
        "dans le formulaire AC-001 avec un délai de résolution maximum de 30 jours.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("4. Indicateurs qualité (KPI)", styles["CustomHeading"]))
    story.append(Paragraph(
        "Taux de conformité produit : objectif 99.5% minimum. "
        "Taux de livraison à temps : objectif 95% minimum. "
        "Nombre de non-conformités client : objectif zéro défaut échappé. "
        "Délai moyen de résolution des non-conformités : objectif 15 jours maximum.",
        styles["CustomBody"]
    ))

    doc.build(story)
    print(f"✅ Créé : {path}")


def create_guide_soumission_client():
    """
    Document 3 : Guide de préparation des soumissions client.
    Simule le processus commercial de DCM.
    """
    path = os.path.join(OUTPUT_DIR, "guide_soumission_client.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = get_styles()
    story = []

    story.append(Paragraph("DCM — Guide de Préparation des Soumissions Client", styles["CustomTitle"]))
    story.append(Paragraph("Document COM-001 | Version 1.5 | Janvier 2024", styles["CustomBody"]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("1. Processus de soumission", styles["CustomHeading"]))
    story.append(Paragraph(
        "Une soumission chez DCM suit un processus structuré en cinq étapes : "
        "réception de la demande de prix, analyse de faisabilité technique, "
        "chiffrage et estimation des coûts, rédaction de l'offre, et soumission au client. "
        "Le délai standard de réponse est de 10 jours ouvrables pour les demandes standard "
        "et 5 jours pour les demandes urgentes.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("2. Documents requis pour une soumission", styles["CustomHeading"]))
    story.append(Paragraph(
        "Plans et spécifications techniques : Les plans doivent être fournis en format PDF "
        "ou DXF avec toutes les tolérances et notes techniques. "
        "Spécification matière : Le client doit préciser la nuance de matériau requise "
        "(ex: Aluminium 7075-T6, Titane 6Al-4V). "
        "Norme de qualité applicable : AS9100, NADCAP ou autre norme spécifique client. "
        "Quantités et délais : Indiquer les quantités par lot et les dates de livraison souhaitées.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("3. Calcul du prix de revient", styles["CustomHeading"]))
    story.append(Paragraph(
        "Le prix de revient d'une pièce chez DCM intègre les éléments suivants : "
        "coût matière (basé sur le cours LME + marge approvisionnement de 15%), "
        "temps d'usinage (taux horaire machine de 85$/h à 120$/h selon l'équipement), "
        "contrôle qualité (forfait de 8% du coût de production), "
        "frais généraux (25% du coût total), "
        "marge commerciale (10% à 20% selon la relation client).",
        styles["CustomBody"]
    ))

    story.append(Paragraph("4. Préparation de la réunion client", styles["CustomHeading"]))
    story.append(Paragraph(
        "Avant toute réunion avec un client comme Airbus ou Bombardier, le chef de projet "
        "doit préparer un dossier comprenant : l'historique des commandes des 24 derniers mois, "
        "le statut de toutes les commandes en cours, les indicateurs qualité du dernier trimestre, "
        "les certificats de conformité des dernières livraisons, "
        "et une proposition commerciale pour les prochains projets.",
        styles["CustomBody"]
    ))

    story.append(Paragraph("5. Contacts clés", styles["CustomHeading"]))
    story.append(Paragraph(
        "Airbus : Responsable approvisionnement — procurement@airbus.com. "
        "Bombardier : Gestionnaire fournisseurs — supply@bombardier.com. "
        "Bell Textron : Coordinateur qualité — quality@belltextron.com. "
        "Pour toute urgence, contacter le directeur commercial de DCM.",
        styles["CustomBody"]
    ))

    doc.build(story)
    print(f" Créé : {path}")


if __name__ == "__main__":
    print("Génération des documents PDF DCM...")
    create_procedure_validation_piece()
    create_norme_qualite_as9100()
    create_guide_soumission_client()
    print(" Tous les documents ont été générés dans docs/pdfs/")