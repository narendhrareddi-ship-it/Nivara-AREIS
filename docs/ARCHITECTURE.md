# NIVARA REALTY — System Architecture (Phase 1)

Free-tier, open-source digital marketing agency stack for Chennai and Andhra Pradesh real estate.

## High-Level Architecture

```mermaid
flowchart TB
    subgraph External["Inbound Channels (Phase 1 Mock)"]
        WEB[Website Forms]
        WA[WhatsApp Mock]
        SOC[Social Mock Webhooks]
    end

    subgraph Orchestration["Workflow Layer"]
        N8N[N8N Self-Hosted]
    end

    subgraph Agents["LangGraph Agent Layer"]
        CEO[CEO Agent]
        MA[Market Analyst]
        CS[Competitor Spy]
        CT[Content Strategist]
        VD[Visual Designer]
        SM[Social Media Manager]
        LQ[Lead Qualification]
        CRM[CRM Agent]
        AN[Analytics Agent]
        ORCH[Orchestrator API :8000]
    end

    subgraph MCP["MCP Servers (Local Stubs)"]
        CRM_MCP[CRM MCP :8001]
        BR_MCP[Browser MCP :8002]
        SOC_MCP[Social MCP :8003]
        WA_MCP[WhatsApp MCP :8004]
        HF_MCP[Higgsfield MCP :8006]
    end

    subgraph Data["Data Layer"]
        SB[(Supabase PostgreSQL)]
    end

    subgraph LLM["Inference (Free)"]
        OLL[Ollama + Llama 3.x]
    end

    WEB --> N8N
    WA --> WA_MCP
    SOC --> SOC_MCP

    N8N --> ORCH
    N8N --> SB

    ORCH --> MA --> CS --> CT --> VD --> SM --> LQ --> CRM --> AN --> CEO
    ORCH --> OLL

    MA --> CRM_MCP
    CS --> BR_MCP
    LQ --> CRM_MCP
    CRM --> CRM_MCP
    AN --> CRM_MCP
    CT --> SOC_MCP
    VD --> HF_MCP
    HF_MCP --> SOC_MCP

    CRM_MCP --> SB
    SOC_MCP --> SB
    WA_MCP --> SB
```

## Component Responsibilities

| Component | Role | Phase 1 Status |
|-----------|------|----------------|
| **Supabase** | CRM database, RLS, REST API | Schema + migrations ready |
| **N8N** | Scheduled workflows, webhooks | 5 importable workflows |
| **LangGraph** | Multi-agent orchestration | 12 agents + CEO synthesis |
| **Ollama** | Local LLM inference | Llama 3.2 default |
| **Higgsfield MCP** | Photo-to-video + social publish | higgsfield-mcp :8006 |
| **MCP Servers** | Tool interfaces for agents/Cursor | 5 servers |
| **Docker Compose** | n8n + ollama + postgres + dashboard | Ready |

## Data Flow: Lead Intake

```mermaid
sequenceDiagram
    participant Form as Website/Ad Form
    participant N8N as N8N Webhook
    participant SB as Supabase
    participant WA as WhatsApp MCP
    participant AG as Lead Qual Agent

    Form->>N8N: POST /webhook/lead-intake
    N8N->>SB: INSERT leads
    N8N->>WA: POST /webhook/message
    WA->>SB: INSERT crm_activity
    N8N-->>Form: { lead_id, success }

    Note over N8N,AG: Hourly crm_sync workflow
    N8N->>SB: SELECT new leads
    N8N->>AG: POST /orchestrate
    AG->>SB: UPDATE leads + log activity
```

## Agent Pipeline (Daily 6 AM)

1. **MarketAnalyst** — Pull projects, analyze regional trends
2. **CompetitorSpy** — Review competitor table + browser stub
3. **ContentStrategist** — Generate content plan from market intel
4. **LeadQualification** — Score new leads
5. **CRM** — Follow-up action plan
6. **Analytics** — Review mock ad performance
7. **CEO** — Executive briefing synthesis

## Security Notes

- All secrets via `.env` (never committed)
- Supabase RLS enabled; service role for backend agents
- N8N basic auth enabled by default
- MCP servers bind to localhost in development

## Directory Structure

```
nivara-digital-marketing/
├── docker-compose.yml
├── supabase/migrations/
├── n8n/workflows/
├── agents/src/nivara/
├── mcp-servers/
└── docs/
```
