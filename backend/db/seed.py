from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.db.connection import sync_engine
from backend.db.models import (
    Base, Client, Employe, Projet, Piece,
    Fournisseur, Commande, StatutProjet, StatutCommande
)


def seed():
    """
    Peuple la base de données avec des données de démo réalistes.
    Exécuté une seule fois au démarrage si la base est vide.
    Simule l'environnement d'une entreprise aéronautique comme DCM.
    """

    with Session(sync_engine) as session:

        # ─── Vérification ─────────────────────────────────
        # Si des clients existent déjà, on ne reseed pas
        if session.query(Client).first():
            print(" Base déjà peuplée — seed ignoré.")
            return

        # ─── Clients ──────────────────────────────────────
        # Grands donneurs d'ordre aéronautiques réels
        airbus = Client(
            nom="Airbus",
            secteur="Aéronautique civile",
            pays="France",
            contact_email="procurement@airbus.com"
        )
        bombardier = Client(
            nom="Bombardier",
            secteur="Aéronautique d'affaires",
            pays="Canada",
            contact_email="supply@bombardier.com"
        )
        bell = Client(
            nom="Bell Textron",
            secteur="Hélicoptères",
            pays="Canada",
            contact_email="ops@belltextron.com"
        )

        session.add_all([airbus, bombardier, bell])
        session.flush()  # Génère les IDs sans commit

        # ─── Employés ─────────────────────────────────────
        marie = Employe(
            nom="Marie Tremblay",
            poste="Chef de projet",
            departement="Ingénierie",
            email="m.tremblay@dcm.com"
        )
        jean = Employe(
            nom="Jean Bouchard",
            poste="Responsable qualité",
            departement="Qualité",
            email="j.bouchard@dcm.com"
        )
        sara = Employe(
            nom="Sara Kowalski",
            poste="Ingénieure production",
            departement="Production",
            email="s.kowalski@dcm.com"
        )

        session.add_all([marie, jean, sara])
        session.flush()

        # ─── Pièces ───────────────────────────────────────
        # Références réalistes — matières et normes aéronautiques
        piece_1 = Piece(
            reference="DCM-AL-7075-001",
            designation="Nervure d'aile aluminium",
            matiere="Aluminium 7075-T6",
            norme="AS9100",
            prix_unitaire=1250.00
        )
        piece_2 = Piece(
            reference="DCM-TI-6AL4V-002",
            designation="Bracket moteur titane",
            matiere="Titane 6Al-4V",
            norme="NADCAP",
            prix_unitaire=3800.00
        )
        piece_3 = Piece(
            reference="DCM-AL-2024-003",
            designation="Panneau fuselage aluminium",
            matiere="Aluminium 2024-T3",
            norme="AS9100",
            prix_unitaire=890.00
        )

        session.add_all([piece_1, piece_2, piece_3])
        session.flush()

        # ─── Fournisseurs ─────────────────────────────────
        fournisseur_1 = Fournisseur(
            nom="Precision Aero Parts",
            pays="Canada",
            certification="AS9100",
            contact_email="sales@precisionaero.ca"
        )
        fournisseur_2 = Fournisseur(
            nom="TitanAero GmbH",
            pays="Allemagne",
            certification="NADCAP",
            contact_email="contact@titanaero.de"
        )

        session.add_all([fournisseur_1, fournisseur_2])
        session.flush()

        # ─── Projets ──────────────────────────────────────
        projet_1 = Projet(
            nom="A320neo — Nervures d'aile",
            description="Fabrication de nervures d'aile pour l'A320neo. Lot de 200 pièces.",
            statut=StatutProjet.en_cours,
            date_debut=datetime(2024, 1, 15),
            date_fin_prevue=datetime(2024, 12, 31),
            budget=850000.00,
            client_id=airbus.id,
            responsable_id=marie.id
        )
        projet_2 = Projet(
            nom="Global 7500 — Brackets moteur",
            description="Usinage de brackets moteur en titane pour le Bombardier Global 7500.",
            statut=StatutProjet.termine,
            date_debut=datetime(2023, 3, 1),
            date_fin_prevue=datetime(2023, 11, 30),
            budget=620000.00,
            client_id=bombardier.id,
            responsable_id=sara.id
        )
        projet_3 = Projet(
            nom="Bell 429 — Panneaux fuselage",
            description="Production de panneaux fuselage pour l'hélicoptère Bell 429.",
            statut=StatutProjet.en_cours,
            date_debut=datetime(2024, 6, 1),
            date_fin_prevue=datetime(2025, 3, 31),
            budget=430000.00,
            client_id=bell.id,
            responsable_id=jean.id
        )

        session.add_all([projet_1, projet_2, projet_3])
        session.flush()

        # ─── Commandes ────────────────────────────────────
        commande_1 = Commande(
            numero="CMD-2024-0001",
            statut=StatutCommande.en_production,
            quantite=50,
            prix_total=62500.00,
            date_commande=datetime(2024, 2, 1),
            date_livraison_prevue=datetime(2024, 8, 1),
            client_id=airbus.id,
            projet_id=projet_1.id,
            piece_id=piece_1.id,
            fournisseur_id=fournisseur_1.id
        )
        commande_2 = Commande(
            numero="CMD-2023-0045",
            statut=StatutCommande.livree,
            quantite=20,
            prix_total=76000.00,
            date_commande=datetime(2023, 4, 10),
            date_livraison_prevue=datetime(2023, 10, 15),
            client_id=bombardier.id,
            projet_id=projet_2.id,
            piece_id=piece_2.id,
            fournisseur_id=fournisseur_2.id
        )
        commande_3 = Commande(
            numero="CMD-2024-0078",
            statut=StatutCommande.en_attente,
            quantite=100,
            prix_total=89000.00,
            date_commande=datetime(2024, 7, 1),
            date_livraison_prevue=datetime(2025, 1, 15),
            client_id=bell.id,
            projet_id=projet_3.id,
            piece_id=piece_3.id,
            fournisseur_id=fournisseur_1.id
        )

        session.add_all([commande_1, commande_2, commande_3])

        # ─── Commit final ──────────────────────────────────
        session.commit()
        print(" Seed terminé — base peuplée avec succès.")


if __name__ == "__main__":
    seed()