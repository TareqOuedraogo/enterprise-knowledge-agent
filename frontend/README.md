
Enterprise Knowledge & Automation Agent
Agent IA d'entreprise multi-sources — SQL · RAG · Email · LangGraph · FastAPI · React
Contexte
Ce projet simule un assistant IA d'entreprise conçu pour le secteur aéronautique.

Un employé pose une question en langage naturel — l'agent orchestre automatiquement plusieurs sources d'information et produit une réponse structurée et professionnelle.
Scénario concret :
Un employé écrit : "Prépare la réunion avec Airbus"
L'agent fait automatiquement :

Interroge la base SQL pour trouver les projets et commandes en cours
Consulte les documents internes pour les procédures qualité AS9100
Génère un email de convocation professionnel
Synthétise tout en une réponse complète structurée

Architecture globale
L'utilisateur interagit via une interface React. Les requêtes passent par FastAPI vers un agent LangGraph qui orchestre trois sources : PostgreSQL pour les données structurées, ChromaDB pour les documents, et un générateur d'emails. GPT-4.1 produit la réponse finale.
Fonctionnalités
Partie 1 — Agent SQL
L'agent reçoit une question en langage naturel, génère automatiquement la requête SQL correspondante, l'exécute sur PostgreSQL et résume les résultats. La base contient des données aéronautiques réalistes : clients Airbus, Bombardier, Bell Textron, projets, commandes, pièces certifiées AS9100.
Partie 2 — Agent RAG Documents
Les documents PDF internes sont indexés dans ChromaDB avec des embeddings OpenAI. L'agent effectue une recherche sémantique et cite les sources dans chaque réponse. Documents inclus : procédure QUA-001, guide qualité AS9100, guide de soumission client.
Partie 3 — Agent Email
L'agent génère des brouillons d'emails professionnels en français et les sauvegarde en JSON. En production, ce module se brancherait sur Microsoft Graph API pour créer de vrais brouillons dans Outlook.
Partie 4 — Orchestration complète
L'agent décide automatiquement quels outils utiliser selon la question. Pour "Prépare la réunion avec Airbus", il active simultanément SQL, RAG et Email et produit une réponse en 5 sections structurées avec sources citées.
Stack technique

Frontend : React 18 avec TypeScript
Backend : FastAPI 0.115 avec Python 3.11
Agent : LangGraph 0.2.28 avec LangChain
LLM : OpenAI GPT-4.1
Base vectorielle : ChromaDB avec text-embedding-3-small
Base de données : PostgreSQL 16 avec pgvector
Infrastructure : Docker et Docker Compose

Lancement rapide
Prérequis : Docker Desktop, Node.js 18+, clé API OpenAI
Cloner le repo :
git clone https://github.com/TareqOuedraogo/enterprise-knowledge-agent.git
cd enterprise-knowledge-agent
Configurer les variables d'environnement :
cp .env.example .env
Éditer .env et ajouter votre clé OpenAI.
Lancer le backend :
docker-compose up --build
Lancer le frontend dans un second terminal :
cd frontend
npm install
npm start
Accéder à l'application sur http://localhost:3000 et la documentation API sur http://localhost:8000/docs
Exemples d'utilisation
Question SQL
Question : "Quels projets avons-nous en cours pour Airbus ?"

Résultat : L'agent interroge PostgreSQL et retourne le projet A320neo, budget 850 000 euros, statut en cours, date de fin prévue décembre 2024.
Question RAG
Question : "Quelle est la procédure de validation AS9100 ?"

Résultat : L'agent recherche dans les PDFs et retourne les 4 étapes de validation avec citations des sources QUA-001 et norme_qualite_as9100.
Question Email
Question : "Rédige un email pour informer l'équipe qualité de la mise à jour QUA-001"

Résultat : L'agent génère un email professionnel complet et sauvegarde le brouillon en JSON.
Orchestration complète
Question : "Prépare la réunion avec Airbus"

Résultat : L'agent active SQL + RAG + Email simultanément et produit une synthèse en 5 sections incluant les données projet, les procédures qualité, les KPIs, le calcul de prix de revient et l'email de convocation.
Tests de sécurité
Six vecteurs d'attaque par injection de prompt ont été testés et bloqués :

Jailbreak DAN classique : bloqué
Roleplay consultant sans restrictions : bloqué
Autorité fictive avec code admin : bloqué
Injection SQL directe dans le chat : bloqué
Injection via contexte RAG : bloqué
Escalade progressive : bloqué

La protection est assurée par un system prompt de sécurité dédié dans LangGraph.
Structure du projet
enterprise-knowledge-agent/
backend/
    main.py — FastAPI entrypoint
    config.py — Settings Pydantic
    agent/
        graph.py — LangGraph graph
        nodes.py — Noeuds agent, tools, synthesis
        tools.py — Tools SQL, RAG, Email
        state.py — AgentState TypedDict
    db/
        models.py — SQLAlchemy ORM
        connection.py — PostgreSQL async
        seed.py — Données de démo
    rag/
        indexer.py — ChromaDB indexing
        retriever.py — Recherche sémantique
    email/
        generator.py — Génération emails
frontend/
    src/App.tsx — Interface React complète
docs/pdfs/ — Documents PDF simulés DCM
scripts/generate_docs.py — Générateur PDFs
docker-compose.yml
.env.example
Améliorations futures

Authentification OAuth/JWT via Microsoft Active Directory
Rate limiting sur FastAPI
Firewall et accès VPN interne uniquement en production
HTTPS avec certificat SSL en production
Emails HTML avec logo DCM et pièces jointes PDF
Microsoft Graph API pour vrais brouillons Outlook
Fine-tuning du modèle sur les emails DCM réels
Mémoire de conversation persistante par session utilisateur

Auteur
Tareq Ouedraogo

Diplômé en Intelligence Artificielle — Collège La Cité, Ottawa, 2026

GitHub : github.com/TareqOuedraogo
Projet développé dans le cadre d'une préparation à un poste de Développeur IA et Automatisation dans le secteur aéronautique.