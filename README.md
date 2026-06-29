# ADIP – Agentic Decision Intelligence Platform

## Team Details

**Team Name:** Pioneers

---

## Project Overview

**ADIP (Agentic Decision Intelligence Platform)** is an AI-powered decision intelligence platform designed to help organizations transform enterprise data into actionable insights and intelligent **Next Best Action (NBA)** recommendations.

The platform ingests data from multiple enterprise sources such as customer interactions, operational records, business documents, equipment data, and sensor readings. It processes this information through an intelligent pipeline consisting of content classification, evidence generation, knowledge integration, business rule evaluation, reasoning, and recommendation generation.

Although demonstrated using the **Energy domain**, the platform is designed with a modular architecture, making it reusable across various industries with minimal customization.

---

## Key Features

* **Intelligent Dataset Import**: Supports CSV, JSON, ZIP, PDF, and TXT files.
* **Automatic Content Classification**: Identifies and categories incoming interaction, asset, and operational data.
* **Evidence Generation Pipeline**: Evaluates trustworthiness, freshness, and normalizes evidence.
* **Knowledge Management**: Cross-references SOPs, compliance guidelines, and vendor manuals.
* **Rule-Based Decision Engine**: Compiles, structures, and executes active business rules.
* **AI-Assisted Reasoning**: Generates inference steps and handles logical contradictions.
* **Explainable Recommendations**: Enriches recommendations with confidence metrics, risk scoring, financial calculations, and action plans.
* **Energy Domain Demonstration**: Shows Solar plants, Wind turbines, Battery, and Transformer maintenance use cases.
* **RESTful API Architecture**: Ready-to-go endpoints for all components.
* **Dockerized Deployment**: Spin up database and storage dependencies with single commands.
* **Responsive Web Interface**: Modern SaaS dashboard layout with interactive AI Copilot (chat and quick prompts) and slide-out recommendation sheets.

---

## Technology Stack

### Frontend
* **Core**: React 19.2, TypeScript 6.0
* **Styling**: Tailwind CSS v4, Radix UI Dialog, Lucide Icons
* **State & Query**: TanStack Query (React Query)
* **HTTP Client**: Axios
* **Visualization**: Recharts (Pie, Area, and Bar charts)
* **Build System**: Vite, TypeScript

### Backend
* **Core Framework**: FastAPI, Python 3.12
* **Data Schemas**: Pydantic v2
* **ORM & Database migration**: SQLAlchemy 2, Alembic
* **Orchestration**: LangChain, LangGraph

### Database & Storage
* **Relational Store**: PostgreSQL
* **Caching & Session State**: Redis
* **Vector Store**: ChromaDB

### AI & Intelligence
* Pluggable LLM Integration (Claude, OpenAI GPT, Gemini, Ollama)
* Evidence Fusion Engine
* Rule-Based Reasoning Engine
* Explainability Metadata Generation

### Deployment
* Docker & Docker Compose

---

## Project Workflow

```text
       Dataset Ingest (CSV, JSON, ZIP, PDF)
                       ↓
            Content Classification
                       ↓
             Validation & Cleaning
                       ↓
                Import Pipeline
                       ↓
             Evidence Generation
                       ↓
            Knowledge Integration (SOPs)
                       ↓
            Business Rule Evaluation
                       ↓
                Reasoning Engine
                       ↓
        Next Best Action Recommendation
                       ↓
             Decision Review (HITL)
                       ↓
                Action Execution
```


---

## Setup Instructions

### Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### Configure Environment
Copy the environment template in the project root:
```bash
cp .env.example .env
```
Update the required configuration values (database credentials, LLM keys, etc.) inside the `.env` file.

### Run Local Backend Services
To launch the backing infrastructure (PostgreSQL, Redis, ChromaDB):
```bash
docker compose up --build
```
This starts:
* **FastAPI Backend**: `http://localhost:8000`
* **Swagger OpenAPI Docs**: `http://localhost:8000/docs`
* **Health API Endpoint**: `http://localhost:8000/api/v1/health`

### Run Frontend Client
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the web dashboard via:
   ```
   http://localhost:5173
   ```

---

## Project Highlights

* **Modular and Reusable**: Core business flows are kept domain-independent; plug in domain adapters to target other sectors (Finance, Healthcare).
* **High-Fidelity AI Assistant**: Interactive ADIP Copilot float widget handles query testing and suggested inquiries instantly.
* **Explainability Native**: Built to justify decisions, showing associated evidence lineage, rule numbers, and calculated confidence directly in drawers.
* **SaaS Layout**: Collagenous sidebar, breadcrumbs, unified notification systems, and responsive theme support.

---

## Future Enhancements

* Multi-domain configuration adapters for Banking and SaaS Customer Success.
* Automated predictive maintenance alerts using real-time anomaly stream tracking.
* Advanced LLM-powered conversational agent integrations.
* Granular Role-Based Access Controls (RBAC) and audit trails for decision reviews.

---

## Additional Notes

This project was developed as part of an Hackathon to demonstrate how enterprise data can be transformed into intelligent, explainable business decisions through a reusable decision intelligence platform.

The current implementation showcases the Energy domain as a reference implementation, while the underlying architecture is designed to support **multiple business domains** through configurable adapters and business rules.
