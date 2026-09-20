# Project 5 — Football Decision Intelligence

**Version:** 1.0  
**Date:** 20 September 2026  
**Status:** ACTIVE — COMMERCIAL PRODUCTION BUILD  
**Internal working name:** Football Decision Intelligence  
**Public product name:** Not yet selected  

---

## 1. Project Purpose

Project 5 is not primarily a portfolio project.

The objective is to build, deploy, market and monetise a real AI product.

Primary success measures are:

- Revenue
- Repeat usage
- Customer retention
- Paid pilots
- Real customer evidence

A completed GitHub repository alone does not make Project 5 successful.

---

## 2. Core Commercial Goal

Build an independent AI product capable of generating income while the following remain in parallel:

1. UK AI employment
2. Innovator Founder pathway
3. Funded PhD applications

The product must therefore have commercial value even if none of the other three pathways succeeds.

---

## 3. Strategic Rule

Every important Project 5 decision must answer at least one of these questions:

1. Does it help us acquire a customer?
2. Does it increase customer value?
3. Does it help the customer return or pay?
4. Does it make the product harder to replace?

If the answer to all four is no, the feature does not belong in the immediate build.

---

## 4. Initial Market

Primary customers:

- Independent football coaches
- Grassroots coaches
- Academy coaches
- Semi-professional coaches
- Independent football analysts
- Smaller football organisations without large analytics departments

Initial market focus:

- United Kingdom first
- International expansion later

---

## 5. Customer Problem

Football coaches regularly face tactical decisions but may lack:

- Dedicated analysts
- Sophisticated tracking systems
- Large analysis budgets
- Time for extensive analysis
- Structured tactical decision-support tools

Existing football products are already strong in areas such as:

- Video analysis
- Tagging
- Match statistics
- Retrospective reporting

Our initial commercial wedge is different.

We focus on helping the coach answer:

> "I have a tactical problem. What are my realistic options, trade-offs, assumptions and risks?"

---

## 6. Job To Be Done

> "When I face a tactical problem, I want to compare realistic options quickly so that I can make a better-informed coaching decision without needing an analytics department."

---

## 7. Core Product

The initial product is a low-data football tactical decision-rehearsal agent.

Core workflow:

```text
MATCH SITUATION
      ↓
TACTICAL PROBLEM
      ↓
COACH OBJECTIVE
      ↓
AVAILABLE OPTIONS
      ↓
OPTION ANALYSIS
      ↓
TRADE-OFF COMPARISON
      ↓
CRITIC / VERIFICATION
      ↓
DECISION BRIEF
      ↓
COACH DECISION
      ↓
ACTUAL OUTCOME
      ↓
DECISION HISTORY
```

---

## 8. V0.1 Customer Experience

The coach should be able to:

1. Create a team profile.
2. Enter a match situation.
3. Describe a tactical problem.
4. Define a tactical objective.
5. Enter possible tactical options or request alternatives.
6. Receive a structured comparison.
7. Save the decision taken.
8. Return later and record the outcome.
9. Review previous tactical decisions.

---

## 9. V0.1 Scenario Input

Initial structured information may include:

- Match minute
- Current score
- Our formation
- Opponent formation
- Yellow cards
- Red cards
- Available substitutions
- Observed tactical problem
- Match objective
- Known player constraints
- Coach observations

The product must initially work without requiring professional tracking data.

---

## 10. Decision Brief Output

The initial decision brief may compare options across:

- Defensive stability
- Attacking threat
- Width
- Midfield control
- Transition exposure
- Personnel suitability
- Fatigue exposure
- Card risk
- Tactical disruption
- Objective alignment

The output should also contain:

- Tactical options
- Main trade-off
- Key assumptions
- Important risks
- What the coach should monitor next
- Confidence level
- Explanation
- Coach decision capture

The output should be concise enough to support decision-making rather than becoming a long AI essay.

---

## 11. Critical AI Trust Rule

The language model must not invent numerical football probabilities.

Unsupported statements such as:

> "Option A gives a 31% probability of conceding."

are prohibited unless that number is produced by an appropriately validated statistical or machine-learning model.

Until validated quantitative models exist, the product may use categories such as:

- Low
- Medium
- High

or transparent structured scoring whose calculation is controlled by our own application logic.

Assumptions must be visible.

The coach remains the final decision-maker.

---

## 12. Product Architecture

Core customer-facing intelligence must exist in our own application.

```text
USER
 ↓
WEB INTERFACE
 ↓
FASTAPI
 ↓
INPUT VALIDATION
 ↓
MATCH-STATE NORMALISER
 ↓
TACTICAL KNOWLEDGE RETRIEVAL
 ↓
SCENARIO / OPTION ENGINE
 ↓
STRUCTURED DECISION ENGINE
 ↓
CRITIC / VERIFIER
 ↓
EXPLANATION LAYER
 ↓
DECISION BRIEF
 ↓
POSTGRESQL
 ↓
DECISION + OUTCOME HISTORY
```

---

## 13. Existing Project Reuse

### Project 1

Reuse:

- RAG principles
- Grounded retrieval
- Source-based reasoning
- FastAPI experience
- Evaluation principles
- Docker
- CI/CD

### Project 2

Reuse:

- Automation
- External integrations
- Workflow design
- Webhook experience
- Delivery automation

### Project 3

Reuse:

- Supervisor patterns
- Specialist reasoning
- Critic
- Bounded revision
- Persistent state
- Failure handling
- Human fallback

### Project 4

Reuse:

- Decision optimisation thinking
- Controlled experimentation
- Baseline comparison
- Ablation methodology
- Robustness testing

### MSc Dissertation

Reuse:

- Football domain foundation
- AWS experience
- Real-time data architecture
- Performance measurement

Project 5 should reuse useful lessons without blindly copying unnecessary complexity.

---

## 14. Production Principle

Complexity must earn its place.

We do not add:

- extra agents
- databases
- services
- frameworks
- queues
- infrastructure

simply because they are technically interesting.

Production priorities are:

1. Customer usefulness
2. Reliability
3. Explainability
4. Evaluation
5. Security
6. Speed
7. Cost control
8. Maintainability

---

## 15. n8n Decision

n8n is not the core customer-facing product.

Core product functionality will live in:

- Python
- FastAPI
- PostgreSQL
- Our decision engine
- Our orchestration
- Our evaluation layer
- Our customer data model

n8n may later support business operations including:

- Customer onboarding
- Email automation
- Lead tracking
- Usage alerts
- Trial reminders
- Internal notifications
- Pilot follow-ups

No paid n8n subscription is required at the beginning.

---

## 16. Initial Technical Stack

### Backend

- Python
- FastAPI
- Pydantic
- Pydantic Settings

### Database

- PostgreSQL

### Retrieval

- pgvector or equivalent when justified

### AI

- OpenAI API through backend services

### Frontend

- Streamlit for the initial MVP

### Testing

- pytest

### Containers

- Docker

### CI/CD

- GitHub Actions

### Deployment

- Low-cost managed hosting

### Payments

- Stripe or another suitable hosted payment provider

### Monitoring

- Application logs
- Error logs
- Usage metrics
- AI request metrics
- AI cost per scenario

---

## 17. Initial Data Model

Expected entities include:

- users
- organisations
- teams
- players
- team_profiles
- scenarios
- scenario_options
- decision_briefs
- coach_decisions
- outcomes
- feedback
- usage_events
- subscriptions

The exact production schema will evolve through migrations.

---

## 18. Product Learning Loop

The strategically important loop is:

```text
SCENARIO
   ↓
OPTIONS
   ↓
COACH DECISION
   ↓
ACTUAL OUTCOME
   ↓
COACH FEEDBACK
   ↓
DECISION HISTORY
   ↓
BETTER FUTURE CONTEXT
```

The objective is not merely to answer questions.

The objective is eventually to build team-specific decision intelligence.

---

## 19. Initial Monetisation

Pricing is experimental until customer behaviour provides evidence.

Initial possibilities include:

### Free Sample

Limited tactical scenarios.

### One-Off Tactical Decision Review

Initial test range:

**£9–£29**

### Founding Coach

Initial test range:

**£9.99–£19.99 per month**

### Coach Pro

Initial test range:

**£20–£39 per month**

### Club Pilot

Initial test range:

**£99–£199**

These prices are hypotheses, not permanently fixed prices.

---

## 20. Concierge MVP

Project 5 may generate revenue before full self-service adoption.

A customer may submit a tactical situation and receive a structured AI-assisted tactical decision report.

During early validation, Adebayo may manually review reports before customer delivery.

The concierge MVP can help us:

- Earn early revenue
- Collect genuine customer scenarios
- Understand customer language
- Discover valuable features
- Improve report quality
- Build trust
- Learn before automating everything

Manual work is acceptable during early commercial validation.

---

## 21. Commercial Metrics

The primary early product metric is:

> Weekly returning coaches who complete tactical scenarios.

Additional metrics include:

- Landing-page visitors
- Visitor-to-signup conversion
- First scenario completion
- Time to first useful result
- Second scenario completion
- Weekly active coaches
- Decisions saved
- Outcomes recorded
- Feedback submitted
- Trial-to-paid conversion
- Paying individual users
- Paid club pilots
- Revenue
- AI cost per scenario
- Customer acquisition source

Registrations alone do not represent commercial success.

---

## 22. Cost Rule

Before meaningful revenue, recurring infrastructure spending should generally remain below approximately:

> £25 per month

unless additional spending directly improves:

- Customer acquisition
- Customer value
- Reliability
- Security
- Payment conversion

Spend money when it buys customers, speed or reliability.

Avoid unnecessary SaaS subscriptions.

---

## 23. V0.1 Scope

The first commercially usable version should support:

- Team profile
- Scenario builder
- Tactical problem
- Tactical objective
- Tactical option generation
- Option comparison
- Decision brief
- Decision persistence
- Outcome recording
- Feedback capture

---

## 24. V0.1 Out of Scope

Do not build these before the core product is validated:

- Computer vision
- Automatic player tracking
- Live camera feeds
- Native mobile application
- Large dashboard suite
- Complex production RL engine
- Professional tracking integrations
- Large multi-agent swarm
- Advanced video processing
- Elaborate social features

These may be reconsidered after customer evidence.

---

## 25. Initial Use Cases

Initial monetisable use cases should focus on lower-complexity situations such as:

### Pre-Match Decision Rehearsal

Example:

> "They normally play 4-3-3. Should we press aggressively or defend in a compact mid-block?"

### Post-Match Counterfactual Review

Example:

> "We conceded after changing shape. What realistic alternatives could we have considered?"

### Tactical Scenario Preparation

Example:

> "How should we respond if the opponent overloads our left side?"

Real-time match decision support may be introduced later after the core system is reliable.

---

## 26. Long-Term Defensibility

The LLM is not the moat.

Potential defensible assets include:

- Structured tactical scenario ontology
- Team profiles
- Coach decision history
- Scenario-to-decision-to-outcome data
- Evaluation framework
- Team-specific tactical memory
- Counterfactual calibration
- Accumulated customer feedback

Long-term direction:

Generic football reasoning

becomes

Team-specific football decision intelligence.

---

## 27. Customer Validation

Customer discovery continues in parallel with development.

We do not wait for every outreach response before building.

Interviews should investigate:

- Hardest tactical decisions
- Existing workflows
- Existing tools
- Current limitations
- Need for alternative-scenario analysis
- Available data
- Trust requirements
- Most useful timing
- Prototype willingness
- Ability to provide sample material
- Budget authority
- Willingness to pay
- Referral opportunities

Customer evidence may change product assumptions.

---

## 28. Evidence Rule

Internal assumptions must never be presented as validated customer findings.

Evidence is classified as:

### ASSUMPTION

Something we currently believe.

### INTERVIEW EVIDENCE

Something a prospective customer directly reports.

### USAGE EVIDENCE

Something actual user behaviour demonstrates.

### PAYMENT EVIDENCE

Someone exchanges money for the product or pilot.

Payment and repeat usage are stronger commercial signals than positive opinions.

---

## 29. Initial Commercial Targets

Targets are aspirational and not guaranteed.

### Private Beta

Target:

**5 October 2026**

### Pilot-Ready Commercial MVP

Target:

**No later than 12 October 2026**

Early commercial evidence goals:

- 10 or more genuine external testers
- 3 or more repeat users
- 5 or more detailed feedback conversations
- First paid individual customer
- First paid organisational pilot
- First revenue

---

## 30. 30-Day Go / Change Test

Approximately 30 days after beta:

### Users try but do not return

Investigate product value.

### Users return but will not pay

Investigate pricing, customer segment and value proposition.

### People visit but do not try

Investigate positioning and onboarding.

### Nobody discovers the product

Investigate distribution and customer acquisition.

### Customers consistently identify a different high-value problem

Consider pivoting.

We do not protect an idea simply because we built it.

---

## 31. Future Vertical Options

Football is the only active commercial vertical now.

Potential future applications of the decision architecture include:

- SEND staffing decision support
- Telecom operations decision support

These should not be built simultaneously with the football MVP.

A future reusable architecture may follow:

```text
STATE
 ↓
CONSTRAINTS
 ↓
OPTIONS
 ↓
ANALYSIS
 ↓
CRITIC
 ↓
HUMAN DECISION
 ↓
OUTCOME
 ↓
MEMORY
```

---

## 32. SEND Principle

Potential future concept:

> Skills-aware and constraint-aware SEND staffing cover decision support.

No real:

- pupil information
- medical information
- safeguarding information
- staff health information
- identifiable school data

will be used without appropriate organisational approval, lawful processing and data-governance controls.

---

## 33. Telecom Principle

Telecom remains commercially attractive because of Adebayo's substantial telecom engineering background.

The present limitations are:

- Data access
- Customer access
- Pilot access
- Enterprise sales-cycle length

If credible anonymised telecom data and an accessible industry pilot become available, commercial priority may be reconsidered.

---

## 34. Innovator Founder Evidence

Project 5 should naturally create evidence including:

- Technical architecture
- Git history
- Founder development contribution
- Competitive research
- Customer interviews
- Product releases
- User activity
- Customer feedback
- Pilot agreements
- Payments
- Invoices
- Revenue
- Testimonials
- Product roadmap
- Cost model
- Growth strategy
- International opportunities

The product is built as a real business first.

Potential visa evidence is a secondary strategic benefit.

---

## 35. AI Employment Benefit

Project 5 should provide credible evidence that Adebayo can:

- Design an AI product
- Translate customer problems into software requirements
- Build production APIs
- Design application architecture
- Deploy AI systems
- Manage LLM costs
- Implement evaluation
- Handle failure cases
- Build reliable agentic workflows
- Work with customers
- Analyse product usage
- Iterate from commercial evidence
- Operate a production AI service

---

## 36. Final Project Rule

Project 5 is:

```text
BUILD
  ↓
DEPLOY
  ↓
MARKET
  ↓
MEASURE
  ↓
CHARGE
  ↓
LEARN
  ↓
IMPROVE
  ↓
SCALE
```

Success hierarchy:

```text
CODE COMPLETED
      ↓
PRODUCT DEPLOYED
      ↓
EXTERNAL USER TRIES IT
      ↓
USER RETURNS
      ↓
USER RECOMMENDS IT
      ↓
USER PAYS
      ↓
ORGANISATION PAYS
      ↓
RECURRING REVENUE
```

Every major product decision should move Project 5 closer to a paying and returning customer.