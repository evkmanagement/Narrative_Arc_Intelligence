# Product Requirements Document (PRD)

## Product Name
Narrative Arc Intelligence Suite

## Version
1.0

## Date
2026-06-29

## Owner
Escalent Hackathon Team

## Document Status
Draft for implementation alignment and stakeholder review

---

## 1. Executive Summary
Narrative Arc Intelligence Suite is an Escalent-branded, one-page, AI-enabled strategic intelligence application that converts EVForward research evidence and external market signals into a structured three-act narrative:

1. Act 1: Where They Are (grounded facts)
2. Act 2: Where They Are Heading (signals and inferences)
3. Act 3: Now What (prioritized recommendations)

The product combines local retrieval (ChromaDB), pluggable LLM generation, and transparent source grounding so strategy teams can generate defensible narratives quickly.

A key enhancement in this version is evidence traceability through report-jump UX: users can click evidence/source links and jump directly to report-level highlights derived from the Hackathon Material corpus.

---

## 2. Problem Statement
Strategic teams face delays and inconsistency when converting fragmented research reports and market events into actionable narrative recommendations.

Current pain points:
- Manual synthesis across multiple EVForward report years and market-event files
- Inconsistent narrative structure between analysts
- Low traceability from recommendations back to source evidence
- Slow scenario testing when macro conditions change

---

## 3. Product Vision
Deliver an Escalent-grade decision-support experience that helps users navigate disruption with AI-enabled insights and expert-ready outputs, while preserving evidence transparency and narrative discipline.

---

## 4. Goals and Non-Goals

### 4.1 Goals
- Generate structured three-act narratives from question + scenario input
- Ensure each output is grounded in retrieved evidence/signals
- Support one-page UX with clear workflow and section navigation
- Provide report-level evidence jump capability
- Maintain local, reproducible ingestion from Hackathon Material files
- Support operational reliability with launcher logging and tests

### 4.2 Non-Goals
- Full enterprise SSO and multi-tenant account management
- Human-in-the-loop workflow orchestration across analyst teams
- Production-grade observability stack (Datadog/Grafana/etc.)
- Real-time collaboration editing

---

## 5. Target Users
- Strategy Consultants
- Insight Managers
- Automotive and Mobility Analysts
- Product Marketing and Demand Planning Leads

---

## 6. User Jobs To Be Done
- "Given a strategic question, help me generate a concise, evidence-backed market narrative."
- "Given a macro scenario, help me understand directional implications quickly."
- "Given recommendations, show me exactly what evidence they are based on."

---

## 7. User Stories
- As an analyst, I want to submit a strategic question and scenario so I can get a structured narrative output.
- As a strategy lead, I want to run validation mode so I can compare inferred outcomes to known market snapshots.
- As a reviewer, I want to jump from source cards to report evidence sections so I can audit grounding.
- As an operator, I want launch logs by stage so I can troubleshoot run failures quickly.

---

## 8. Scope

### 8.1 In Scope (Current)
- FastAPI backend with versioned endpoints
- Vanilla JS frontend, one-page landing UX
- Escalent-inspired branding system (palette, layout, CTA style)
- Local ingestion from Hackathon Material report files
- Local Chroma retrieval and LLM generation
- Evidence report summary endpoint and report-jump UI
- Automated API tests
- Launcher runtime log file at project root
- PDF export formatting with brand templates

### 8.2 Out of Scope (Current)
- External document upload by end users
- Authentication/authorization
- Advanced filtering and semantic report search UI
- PDF export formatting with brand templates

### 8.3 Tech Stack List
- Language and Runtime:
  - Python 3.11 (primary runtime)
  - Node-free frontend runtime (browser-native)
- Backend:
  - FastAPI
  - Uvicorn
  - Pydantic
  - python-dotenv
- AI and LLM Integrations:
  - Azure OpenAI
  - OpenAI
  - Anthropic Claude
  - Google Gemini (google-generativeai)
- Retrieval and Data Layer:
  - ChromaDB (local persistent vector store)
  - Local text corpora from Hackathon Material files
  - Generated knowledge artifacts in knowledge/evidence_bank.txt and knowledge/market_events.txt
- Frontend:
  - HTML5
  - CSS3
  - Vanilla JavaScript (ES6+)
  - Escalent-inspired one-page landing UI system
- Testing and Quality:
  - pytest
  - FastAPI TestClient-based API tests
- Launch and Operations:
  - run.py launcher with interpreter switching and staged execution
  - Root-level run.log runtime log file


---

## 9. Functional Requirements

### 9.1 Input and Orchestration
- User can enter a question (10 to 500 chars)
- User can select one scenario:
  - Baseline - Current Market Conditions
  - Federal EV Subsidies Roll Back
  - Gas Prices Spike 20%

### 9.2 Narrative Generation
- System must return (these 3 in vertical/side by side o UI):
  - Act 1 FACT items
  - Act 2 SIGNAL and INFERENCE items
  - Act 3 ranked recommendations
  - source metadata list
- If evidence is insufficient, system must degrade gracefully with explicit guidance.

### 9.3 Evidence and Report Jump (Open ref. file/report and highlight with yellow as a pop-up overlay)
- Backend must provide report summary data across:
  - Extracted Facts from EVForward Reports
  - Extrernal Market Signals
- Frontend must render clickable report chips
- Clicking a report chip must jump to the report detail section
- Clicking "Jump to report evidence" on source cards must jump to best-matching report by year/category

### 9.4 Validation Mode
- User can trigger backtest endpoint
- UI must render validation output and actual snapshot cards

### 9.5 Export
- User can export latest narrative payload as PDF. - PDF export formatting with brand templates

### 9.6 Logging
- Launcher must write stage-based logs to root run.log
- Logs should include interpreter checks, mode resolution, ingest selection, step execution, exit codes, and exception traces

---

## 10. Non-Functional Requirements

### 10.1 Performance
- API health/config endpoints should respond in under 300 ms locally
- Narrative response latency target: under 12 seconds (dependent on selected LLM provider)

### 10.2 Reliability
- API should gracefully handle malformed LLM JSON via fallback behavior
- Launcher should avoid interactive EOF traceback and apply safe defaults

### 10.3 Security
- Secrets must remain in environment variables only
- .env must not be committed
- No sensitive secrets surfaced in UI

### 10.4 Maintainability
- Backend and frontend interfaces must remain testable via automated tests
- Ingestion source of truth must remain Hackathon Material directory

---

## 11. Data Sources and Content Model

### 11.1 Primary Inputs
- Hackathon Material/Extracted Facts from EVForward Reports/*.txt
- Hackathon Material/Extrernal Market Signals/*.txt

### 11.2 Derived Artifacts
- knowledge/evidence_bank.txt
- knowledge/market_events.txt
- chroma_db collections:
  - evidence_bank
  - market_events

### 11.3 Output Schema (Narrative)
- question
- scenario
- act1[]
- act2[]
- act3[]
- sources[]
- meta (request_id, generated_at_utc, provider, latency_ms)

---

## 12. API Requirements

### 12.1 Core APIs
- GET /api/health
- GET /api/v1/health
- GET /api/config
- GET /api/v1/config
- GET /api/scenarios
- GET /api/v1/scenarios
- POST /api/analyze
- POST /api/v1/analyze
- POST /api/backtest
- POST /api/v1/backtest

### 12.2 Evidence Jump API
- GET /api/v1/evidence/reports
- Returns report_id, title, category, year, file_name, entry_count, highlights[]

---

## 13. UX and Branding Requirements

### 13.1 Design Direction
- One-page landing experience with section navigation
- Escalent-guided visual language aligned to site reference:
  - Base text color: #3f3f3f
  - Base background color: #ffffff
  - Brand purple anchor: #7a00df (with darker support shades for hierarchy)
  - Supporting palette can include teal/coral accents for call-to-action and signal differentiation
  - White-on-dark hero treatment where needed
- Typography and baseline styling requirements:
  - Primary body font family: HelveticaNeue, sans-serif
  - Base html/body line-height and readable density equivalent to medium/1.2 baseline
  - Global box model normalization: box-sizing border-box for root and all elements
- Tokenized design system requirements:
  - Standardized font size scale: 13, 16, 20, 36, 42
  - Standardized spacing scale: 0.44rem, 0.67rem, 1rem, 1.5rem, 2.25rem, 3.38rem, 5.06rem
  - Standardized shadow scale: natural, deep, sharp, outlined, crisp
  - Gradients may be used selectively for hero and CTA emphasis, not for dense data sections

### 13.2 Mandatory UI Behaviors
- Remove provider profile detail from visible header
- Keep status chip visible
- Report jump section must be discoverable and interactive
- Smooth scroll jump between sections and reports
- Mobile-first responsive behavior preserved
- Landing hero module requirements:
  - Hero wrapper behavior equivalent to .fma (positioned context with layered foreground content)
  - Optional bottom-center carat affordance behavior equivalent to .fma-carat for first-scroll cue
  - Hero must preserve high contrast and clear primary CTA
- Evidence jump interaction requirements:
  - Clicking a report chip must scroll to the corresponding report panel
  - Clicking source jump controls must route to best-match report-year section
  - Target report panel must use temporary visual highlight state after jump

### 13.3 One-Page Template Requirements
- Section order and template structure:
  - Hero and value proposition (Escalent messaging aligned)
  - Analysis Brief and scenario controls
  - Three-act narrative workspace -vertical (Act 1, Act 2, Act 3)
  - Evidence File/Report Jump hub
  - Validation output and actual snapshot panel
- Navigation behavior:
  - Persistent intra-page anchor navigation for key sections
  - Smooth scrolling between anchors
  - Consistent section IDs for deep-linking readiness

### 13.4 Accessibility
- Keyboard operability for controls and jump chips
- Visible focus states
- Semantic headings and section anchors
- Motion and interaction must remain usable with reduced motion preferences when enabled

---

## 14. Success Metrics
- Narrative generation completion rate > 95% per local run session
- Report jump click-through rate > 40% of sessions using generated output
- Zero launcher EOF tracebacks in standard run flow
- Automated test suite pass rate 100%

---

## 15. Analytics and Observability
- Launcher run.log captures runtime stage diagnostics
- API request metadata includes request IDs and latency
- Future enhancement: add frontend event tracking for report-jump usage

---

## 16. QA and Acceptance Criteria

### 16.1 Functional Acceptance
- User can generate narrative successfully from default demo question
- User can run validation mode and view outputs
- User can click source jump and land on matching report block
- User can click report chips and jump to report details

### 16.2 Regression Acceptance
- Existing API endpoints remain operational
- Tests pass in project Python 3.11 environment

### 16.3 Test Command
- .venv311\\Scripts\\python.exe -m pytest -q

---

## 17. Risks and Mitigations
- Risk: Parsing quality variance from semi-structured report files
  - Mitigation: normalization rules, filters, and dedupe in ingestion
- Risk: LLM provider failures or malformed responses
  - Mitigation: fallback parsing and heuristic fallback narrative path
- Risk: Branding drift over iterations
  - Mitigation: centralized design tokens and periodic Escalent site alignment review

---

## 18. Milestones
- M1: Core API and ingestion stabilization (Done)
- M2: Escalent landing UX and report jump interaction (Done)
- M3: Expanded analytics and enterprise auth (Planned)

---

## 19. Open Questions
- Should report jump support direct deep-link URLs for sharing (hash-based route)?
- Should evidence cards include file open/download links for full report text?
- Should we add persona-specific prompt presets as first-class UI controls?

---

## 20. Appendix: Current Implementation Notes
- Root launcher log file exists at run.log
- Evidence report endpoint aggregates yearly report summaries from Hackathon Material
- Frontend is single-page with jump navigation and evidence report detail sections
