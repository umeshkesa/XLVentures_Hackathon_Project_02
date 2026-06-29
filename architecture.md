# Agentic Decision Intelligence Platform (ADIP) Architecture

## 1. Project Overview

The **Agentic Decision Intelligence Platform (ADIP)** is a domain-agnostic, enterprise-grade multi-agent architecture designed to process enterprise interactions and organizational knowledge, analyze them against corporate guidelines and business rules, perform structured reasoning, and output explainable Next Best Action recommendations with human-in-the-loop oversight.

* **Vision**: Transform unstructured data (emails, CRM notes, sensor logs, maintenance records) into concrete, actionable, and explainable recommendations.
* **Core Philosophy**: A strict, planner-first orchestration model combined with a domain-agnostic core. All business logic is loaded dynamically via Domain Plugins rather than hardcoded.

---

## 2. Core Architectural Principles

All modules and components adhere strictly to the following principles:

1. **Planner First**: The Planner Agent controls all workflow orchestration. Specialized agents do not run independently; they are orchestrated dynamically based on user goals and system state.
2. **Domain Agnostic**: The platform contains no hardcoded business rules or domain models. Domain packages (such as Energy Operations, Healthcare, or Finance) are plugged in dynamically.
3. **Capability Driven**: The Planner discovers and invokes agents and tools using defined capability metadata rather than hardcoded bindings or references.
4. **Explainability**: Recommendations must supply a complete trace of proof including backing evidence, relevant knowledge references, triggered business rules, alternative actions considered, risk assessments, and calculated confidence scores.
5. **Human-in-the-Loop (HITL)**: All generated next-best actions undergo human review before execution, governed by configurable policy rules.
6. **Extensibility**: Addition of new agents, models, rules, or entire enterprise domains requires zero modifications to the ADIP platform core.

---

## 3. High-Level System Diagram

```
+---------------------------------------------------------------------------------+
|                                 FRONTEND                                        |
| React 19.2 + TypeScript + Tailwind CSS v4 + Recharts Dashboard Client           |
| UI Modules: Dashboard | Customers | Energy Assets | Import Center | Copilot    |
+---------------------------------------------------------------------------------+
                                      |
                                      | REST APIs (JSON / Swagger)
                                      v
+---------------------------------------------------------------------------------+
|                                BACKEND CORE                                     |
| FastAPI Gateway + Uvicorn + Dependency Injection                              |
+---------------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
+------------------+         +------------------+         +------------------+
|  REGISTRY LAYER  |         |  ORCHESTRATION   |         |  PIPELINE ENGINES|
|  Agent Registry  |         |  Planner Agent   |         | Reasoning Engine |
|  Tool Registry   |-------->|  Workflow Engine |-------->| Confidence Engine|
|  Plugin Registry |         |  Session Manager |         | Recommend Engine |
+------------------+         +------------------+         +------------------+
         |                            |                            |
         v                            v                            v
+------------------+         +------------------+         +------------------+
|  DATA & MEMORY   |         |    KNOWLEDGE     |         |  RULES & POLICY  |
|  Memory Manager  |         |  Knowledge Mgr   |         |   Rule Manager   |
|  Evidence Fusion |         |  Document Ingest |         |   Policy Engine  |
+------------------+         +------------------+         +------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|                                PLUGINS LAYER                                    |
| Domain Plugins: Energy & Climate (Solar, Wind, Batteries, Transformers, Sensors)|
| Agent Plugins: SQL Agent | PDF Parser | OCR Agent | Search Agent                |
+---------------------------------------------------------------------------------+
```

---

## 4. Layered System Architecture

### 4.1. Frontend Layer
Built with a modern web stack (Vite + React 19.2 + TypeScript 6.0 + Tailwind CSS v4) configured as an enterprise SaaS workspace:
* **Shell & Collapsible Sidebar**: Fast navigation between Dashboard, Customers, Assets, Import Center, Interactions, Knowledge, Evidence, Reasoning, Recommendations, and Settings.
* **Interactive AI Copilot (AIAssistant)**: Floating assistant equipped with instant conversation history, suggested inquiries, typing states, and custom Markdown table rendering.
* **Recommendation Center**: Rich card-based view displaying prioritization, confidence levels, financial yields, and slide-out details detailing lineage connections and action plans.
* **Import Center**: Drag-and-drop file ingestion displaying dynamic workflow stages (Classification → Validation → Import → Evidence Generation → Reasoning → Recommendation → Completed).

### 4.2. Orchestration & Planner Layer
* **Planner Agent**: Interprets goals, builds execution graphs, and triggers specialized child agents.
* **Workflow Engine**: Executes plans asynchronously, managing status transitions and error boundaries.

### 4.3. Registry & Plugin Framework
* **Plugin Manager**: Discovers, validates, installs, loads, sandboxes, and initializes external extensions. Includes dependency graph management and DFS cycle checking.
* **Sandboxing**: Runs plugins in isolated namespaces with CPU, Memory, Storage, and Timeout limits.

### 4.4. Memory & Evidence Layer
* **Memory Service**: The single public entry point for persistent interaction memory, cache tracking, version state, and audit tracing.
* **Evidence Fusion Engine**: Ingests multi-source evidence, deduplicates records, correlates timelines, and utilizes consensus engines to determine composite trust and reliability weights.

### 4.5. Rules & Policy Layer
* **Rule Manager**: Compiles and evaluates business rules, prioritizing logic categories, and detecting conflicting outcomes.
* **Policy Engine**: Validates domain scopes and enforces organizational governance constraints.

### 4.6. Reasoning, Recommendations, & Explainability
* **Reasoning Engine**: Formulates hypotheses, executes inference chains, detects logical contradictions, and compares alternatives via multi-criteria ranking.
* **Recommendation Engine**: Packages decisions into concrete Next Best Actions, computing cost-savings offsets and generating suggested checklists.
* **Explainability Engine**: Generates comprehensive natural language explanations detailing *why* specific rules triggered, *why* certain weights were applied, and *how* a confidence rating was calculated.

---

## 5. End-to-End Workflow & Data Flow

1. **Ingest / Input**: A user imports raw data (e.g. transformer sensor metrics) via the **Import Center** or query via **AIAssistant**.
2. **Orchestration Plan**: The **Planner** parses the request and queries the **Agent & Tool Registries** to assemble an execution plan.
3. **Information Retrieval**: The planner calls the **Memory Manager** and **Knowledge Manager** to retrieve historical context and standard operating procedures (SOPs).
4. **Evidence Collection**: The **Evidence Fusion Engine** validates and normalizes incoming logs, generating correlated evidence records with reliability weights.
5. **Rules Application**: The **Rule Manager** executes active business rules against the consolidated evidence.
6. **Reasoning Pipeline**: The **Reasoning Engine** structures hypotheses, validates compliance limits, resolves contradictions, and generates alternative actions.
7. **Recommendation Formulation**: The **Recommendation Engine** calculates confidence scores, predicts cost/savings metrics, creates a list of suggested tasks, and compiles explainability meta-tokens.
8. **Decision Review (HITL)**: The compiled action is stored in the **Decision Review Layer** pending manager approval.
9. **Outcome Tracking & Learning**: Once approved and executed, outcomes are captured by the **Memory Layer** for continuous framework reinforcement.

## Decision Pipeline 

Every recommendation follows the same transparent workflow.

+---------------------------------------------------------------------------------------+
|                                    FRONTEND                                           |
| React + TypeScript + Tailwind + TanStack Query + Recharts                            |
+---------------------------------------------------------------------------------------+
                                        │
                                   REST APIs
                                        │
+---------------------------------------------------------------------------------------+
|                               FASTAPI BACKEND                                         |
+---------------------------------------------------------------------------------------+
                                        │
                              API Gateway / Router
                                        │
                                        ▼
+---------------------------------------------------------------------------------------+
|                             PLANNER AGENT (Brain)                                     |
| Understand User Intent | Task Planning | Workflow Planning                            |
+---------------------------------------------------------------------------------------+
                                        │
                                        ▼
+---------------------------------------------------------------------------------------+
|                         CAPABILITY AGENT / DISCOVERY                                  |
| Discovers Available Agents | Tools | Plugins | Domain Capabilities                    |
+---------------------------------------------------------------------------------------+
                                        │
                                        ▼
+---------------------------------------------------------------------------------------+
|                           WORKFLOW ORCHESTRATOR                                       |
| Executes Plan | Coordinates Agents | Session Context | State                          |
+---------------------------------------------------------------------------------------+
           │                │                │                 │
           ▼                ▼                ▼                 ▼
   Knowledge Agent   Evidence Agent   Rules Agent     Energy Agent
           │                │                │                 │
           └────────────────┴────────────────┴─────────────────┘
                                │
                                ▼
+---------------------------------------------------------------------------------------+
|                             REASONING ENGINE                                          |
| Evidence Fusion | Context Builder | LLM | Confidence | Ranking                        |
+---------------------------------------------------------------------------------------+
                                │
                                ▼
+---------------------------------------------------------------------------------------+
|                          RECOMMENDATION ENGINE                                        |
| Generate Next Best Action | Alternatives | Business Impact                            |
+---------------------------------------------------------------------------------------+
                                │
                                ▼
+---------------------------------------------------------------------------------------+
|                     EXPLAINABILITY + HUMAN REVIEW                                     |
| Why? | Traceability | Confidence | HITL Approval                                      |
+---------------------------------------------------------------------------------------+
                                │
                                ▼
+---------------------------------------------------------------------------------------+
|                           ACTION EXECUTION                                            |
+---------------------------------------------------------------------------------------+

---

## 6. Technology Stack Summary

* **Backend Framework**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic
* **Orchestration**: LangGraph, LangChain
* **Storage Systems**:
  - *Relational Database*: PostgreSQL (Transactional memory, rule definitions, and entities)
  - *Vector Database*: ChromaDB (Semantic knowledge search, document embeddings)
  - *Caching Layer*: Redis (Session caching, execution-stage temporary tokens)
* **Frontend Web Stack**: React 19.2, TypeScript 6.0, Tailwind CSS v4, Radix UI Dialog, Recharts (Pie, Bar, Area charts)
* **Deployment & Environments**: Docker, Docker Compose
