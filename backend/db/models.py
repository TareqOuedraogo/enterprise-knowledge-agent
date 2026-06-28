from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Text, Enum
)
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    pass


class StatutProjet(str, enum.Enum):
    en_cours = "en_cours"
    termine = "termine"
    suspendu = "suspendu"


class StatutCommande(str, enum.Enum):
    en_attente = "en_attente"
    en_production = "en_production"
    livree = "livree"
    annulee = "annulee"


# ─── Tables ───────────────────────────────────────────────

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    secteur = Column(String(100))  # ex: aéronautique, défense
    pays = Column(String(100))
    contact_email = Column(String(150))
    created_at = Column(DateTime, default=datetime.utcnow)

    projets = relationship("Projet", back_populates="client")
    commandes = relationship("Commande", back_populates="client")


class Employe(Base):
    __tablename__ = "employes"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    poste = Column(String(100))
    departement = Column(String(100))
    email = Column(String(150))

    projets = relationship("Projet", back_populates="responsable")


class Projet(Base):
    __tablename__ = "projets"

    id = Column(Integer, primary_key=True)
    nom = Column(String(200), nullable=False)
    description = Column(Text)
    statut = Column(Enum(StatutProjet), default=StatutProjet.en_cours)
    date_debut = Column(DateTime)
    date_fin_prevue = Column(DateTime)
    budget = Column(Float)
    client_id = Column(Integer, ForeignKey("clients.id"))
    responsable_id = Column(Integer, ForeignKey("employes.id"))

    client = relationship("Client", back_populates="projets")
    responsable = relationship("Employe", back_populates="projets")
    commandes = relationship("Commande", back_populates="projet")


class Piece(Base):
    __tablename__ = "pieces"

    id = Column(Integer, primary_key=True)
    reference = Column(String(50), unique=True, nullable=False)
    designation = Column(String(200))
    matiere = Column(String(100))  # ex: aluminium 7075, titane
    norme = Column(String(100))    # ex: AS9100, NADCAP
    prix_unitaire = Column(Float)

    commandes = relationship("Commande", back_populates="piece")


class Fournisseur(Base):
    __tablename__ = "fournisseurs"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    pays = Column(String(100))
    certification = Column(String(100))  # ex: AS9100, ISO9001
    contact_email = Column(String(150))

    commandes = relationship("Commande", back_populates="fournisseur")


class Commande(Base):
    __tablename__ = "commandes"

    id = Column(Integer, primary_key=True)
    numero = Column(String(50), unique=True, nullable=False)
    statut = Column(Enum(StatutCommande), default=StatutCommande.en_attente)
    quantite = Column(Integer)
    prix_total = Column(Float)
    date_commande = Column(DateTime, default=datetime.utcnow)
    date_livraison_prevue = Column(DateTime)

    client_id = Column(Integer, ForeignKey("clients.id"))
    projet_id = Column(Integer, ForeignKey("projets.id"))
    piece_id = Column(Integer, ForeignKey("pieces.id"))
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"))

    client = relationship("Client", back_populates="commandes")
    projet = relationship("Projet", back_populates="commandes")
    piece = relationship("Piece", back_populates="commandes")
    fournisseur = relationship("Fournisseur", back_populates="commandes")