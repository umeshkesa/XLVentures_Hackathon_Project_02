#  Intelligent Next Best Action Platform 
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![React](https://img.shields.io/badge/React-19.2-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6)
![LangChain](https://img.shields.io/badge/LangChain-Agent_Framework-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Orchestration-purple)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-orange)
![Redis](https://img.shields.io/badge/Redis-Cache-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![License](https://img.shields.io/badge/License-Hackathon-orange)

## Team Details

**Team Name:** Pioneers

---

## Project Overview

**ADIP (Agentic Decision Intelligence Platform)** is an AI-powered decision intelligence platform designed to help organizations transform enterprise data into actionable insights and intelligent **Next Best Action (NBA)** recommendations.

The platform ingests data from multiple enterprise sources such as customer interactions, operational records, business documents, equipment data, and sensor readings. It processes this information through an intelligent pipeline consisting of content classification, evidence generation, knowledge integration, business rule evaluation, reasoning, and recommendation generation.

Although demonstrated using the **Energy domain**, the platform is designed with a modular architecture, making it reusable across various industries with minimal customization.

---
## Objectives

- Build a reusable Agentic Decision Intelligence Platform.
- Generate intelligent Next Best Actions.
- Combine enterprise knowledge, business rules, and AI reasoning.
- Support explainable and trustworthy decision making.
- Enable domain extensibility using plugin architecture.
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
## Reusable Agentic Decision Intelligence Platform Architecture
```text
+=============================================================================================================+
|                                          USER INTERFACES                                                    |
+=============================================================================================================+
|                                                                                                             |
|  Customer Portal            Business Admin Portal             Platform Admin Portal                         |
|                                                                                                             |
|  • Dashboard                • Dashboard                      • Plugin Registry                              |
|  • My Assets                • Customers                      • Agent Registry                               |
|  • Interactions             • Assets                         • Domain Packages                              |
|  • Recommendations          • Import Center                  • Workflow Templates                           |
|  • Evidence                 • Knowledge Center               • Business Rules                               |
|  • Support                  • Decision Review                • Model Configuration                          |
|                             • Action Manager                 • Capability Registry                          |
+=============================================================================================================+
                                                │
                                                │ REST / WebSocket
                                                ▼
+=============================================================================================================+
|                                       API GATEWAY (FastAPI)                                                 |
|-------------------------------------------------------------------------------------------------------------|
| Authentication | Validation | Authorization | Logging | Rate Limiting | Swagger | Error Handling            |
+=============================================================================================================+
                                                │
                                                ▼
+=============================================================================================================+
|                                          PLANNER AGENT                                                      |
|-------------------------------------------------------------------------------------------------------------|
| • Understand User Goal                                                                                      |
| • Analyze Business Context                                                                                  |
| • Create Execution Plan                                                                                     |
| • Ask Capability Agent for required capabilities                                                            |
+=============================================================================================================+
                                                │
                                                ▼
+=============================================================================================================+
|                                     CAPABILITY AGENT                                                        |
|-------------------------------------------------------------------------------------------------------------|
| • Discover Required Capabilities                                                                            |
| • Match Goal → Capability                                                                                   |
| • Query Capability Registry                                                                                 |
| • Select Suitable Agents                                                                                    |
| • Resolve Dependencies                                                                                      |
+=============================================================================================================+
                                                │
                                                ▼
+=============================================================================================================+
|                                     CAPABILITY REGISTRY                                                     |
|-------------------------------------------------------------------------------------------------------------|
| Agent Registry | Tool Registry | Plugin Registry | Domain Registry | Workflow Registry                      |
+=============================================================================================================+
                                                │
                                                ▼
+=============================================================================================================+
|                                     ORCHESTRATION ENGINE                                                    |
|-------------------------------------------------------------------------------------------------------------|
| • Execute Agent Pipeline                                                                                    |
| • Parallel Agent Execution                                                                                  |
| • Retry / Recovery                                                                                          |
| • Session Management                                                                                        |
+=============================================================================================================+
                                                │
                                                ▼
+=============================================================================================================+
|                                       SPECIALIZED AGENTS                                                    |
+=============================================================================================================+
|                                                                                                             |
|  Import Agent                                                                                               |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Classification Agent                                                                                       |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Entity Extraction Agent                                                                                    |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Evidence Generation Agent                                                                                  |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Knowledge Retrieval Agent (RAG)                                                                            |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Business Rule Agent                                                                                        |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Reasoning Agent (LLM + Rules)                                                                              |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Recommendation Agent                                                                                       |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Explainability Agent                                                                                       |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Human-in-the-Loop Agent                                                                                    |
|        │                                                                                                    |
|        ▼                                                                                                    |
|  Execution Agent                                                                                            |
+=============================================================================================================+
                                                │
                                                ▼
+=============================================================================================================+
|                                 DECISION INTELLIGENCE LAYER                                                 |
|-------------------------------------------------------------------------------------------------------------|
| Context Builder | Confidence Engine | Risk Analysis | Opportunity Detection                                 |
| Missing Information Detection | Alternative Actions | Next Best Action Generator                            |
+=============================================================================================================+
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          ▼                     ▼                     ▼
+================================+ +================================+ +================================+
|        SHARED MEMORY           | |      KNOWLEDGE LAYER           | |     BUSINESS RULE ENGINE       |
|--------------------------------| |--------------------------------| |--------------------------------|
| Customer Memory                | | SOPs                           | | Rule Evaluation                |
| Session Memory                 | | Playbooks                      | | Policy Engine                  |
| Conversation History           | | Manuals                        | | SLA Rules                      |
| Recommendation History         | | Customer History               | | Compliance Rules               |
| Organizational Context         | | CRM Data                       | | Priority Rules                 |
+================================+ +================================+ +================================+
                          │                     │                     │
                          └─────────────────────┼─────────────────────┘
                                                ▼
+=============================================================================================================+
|                                          LLM LAYER                                                          |
|-------------------------------------------------------------------------------------------------------------|
| OpenAI / Gemini / OpenRouter / Ollama                                                                       |
| Prompt Builder | Structured Output | JSON Validation | Guardrails | Function Calling                        |
+=============================================================================================================+
                                                │
                                                ▼
+=============================================================================================================+
|                                   PLUGIN & DOMAIN ARCHITECTURE                                              |
|-------------------------------------------------------------------------------------------------------------|
| Domain Packages: Energy | Healthcare | Manufacturing | Customer Success | Banking | Insurance               |
|                                                                                                             |
| Each Domain Package Provides:                                                                               |
| • Domain Ontology                                                                                           |
| • Specialized Agents                                                                                        |
| • Business Rules                                                                                            |
| • Prompt Templates                                                                                          |
| • Knowledge Sources                                                                                         |
| • Workflows                                                                                                 |
+=============================================================================================================+
                                                │
                                                ▼
+=============================================================================================================+
|                                      DATA & INFRASTRUCTURE                                                  |
|-------------------------------------------------------------------------------------------------------------|
| PostgreSQL | ChromaDB | Redis | Docker | FastAPI | Background Workers | Object Storage                      |
+=============================================================================================================+
```
---
## Project Workflow

```text
      Customer Interaction / Email / Chat / CRM / Meeting
                    │
                    ▼
              API Gateway
                    │
                    ▼
              Planner Agent
                    │
                    ▼
            Capability Agent
                    │
                    ▼
         Capability Registry Lookup
                    │
                    ▼
      Discover Required Agents & Tools
                    │
                    ▼
          Orchestration Engine
                    │
                    ▼
 Import → Classification → Entity Extraction
                    │
                    ▼
         Evidence Generation Agent
                    │
                    ▼
       Knowledge Retrieval Agent
                    │
                    ▼
        Business Rule Agent
                    │
                    ▼
      Reasoning Agent (LLM + Rules)
                    │
                    ▼
       Recommendation Agent
                    │
                    ▼
      Explainability Agent
                    │
                    ▼
     Human-in-the-Loop Review
                    │
                    ▼
     Next Best Action Recommendation
                    │
                    ▼
      Store Results in Shared Memory
                    │
                    ▼
      Future Recommendations Improve
```
## Security

- JWT Authentication
- Role-Based Access Control
- Audit Logging
- Human Approval before Execution
- Secure Plugin Isolation
---
## Business Outcomes

• Faster enterprise decision making

• Reduced manual investigation

• Improved operational efficiency

• Explainable AI recommendations

• Lower response time for critical incidents

• Better utilization of enterprise knowledge

---
## Hackathon Evaluation Mapping

✅ Planner-Based Agent Orchestration

✅ Reusable Plugin Architecture

✅ Capability Registry

✅ Shared Memory

✅ Enterprise Knowledge Retrieval

✅ Business Rules Engine

✅ AI Reasoning

✅ Explainability

✅ Human-in-the-Loop

✅ Extensible Domain Packages

✅ Modern User Experience

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

* Automated predictive maintenance alerts using real-time anomaly stream tracking.
* Advanced LLM-powered conversational agent integrations.
* Granular Role-Based Access Controls (RBAC) and audit trails for decision reviews.

---

## Additional Notes

This project was developed as part of an Hackathon to demonstrate how enterprise data can be transformed into intelligent, explainable business decisions through a reusable decision intelligence platform.

The current implementation showcases the Energy domain as a reference implementation, while the underlying architecture is designed to support **multiple business domains** through configurable adapters and business rules.
