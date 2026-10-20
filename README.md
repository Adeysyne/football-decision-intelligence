# Football Decision Intelligence

Football Decision Intelligence (FDI) is a low-data tactical decision-support platform for football coaches.

The product helps coaches compare realistic tactical interventions using structured match information such as the score, match minute, formations, tactical objective, available personnel, disciplinary constraints and relevant match observations.

FDI is designed to support coaching judgement rather than replace it.

## Current Stage

FDI is currently deployed as a private-beta product.

Production website:

https://footballdecisionintelligence.com

Current automated regression baseline:

**107 passing tests**

## The Problem

During a match, a coach may have several reasonable tactical options available.

For example:

- make a substitution;
- change structure;
- protect a lead;
- add support around a vulnerable player;
- increase attacking threat; or
- maintain the current shape.

Each option may solve one problem while creating another.

FDI provides a structured way to compare those trade-offs.

## Decision Workflow

The current workflow is:

1. Capture the match situation.
2. Identify the coach's tactical objective.
3. Apply tactical and personnel constraints.
4. Generate feasible interventions.
5. Evaluate the available options.
6. Compare tactical trade-offs.
7. Provide an optional verified AI explanation.
8. Leave the final decision with the coach.

## Evaluation Dimensions

Options are currently assessed across:

- Defensive Stability
- Transition Security
- Attacking Threat
- Personnel Fit
- Wide Control
- Tactical Continuity
- Midfield Control
- Objective Alignment

## Technical Approach

The current product combines:

- structured tactical-state modelling;
- deterministic feasibility constraints;
- objective-aware evaluation;
- observation-aware calibration;
- multi-dimensional scoring;
- AI-supported explanation;
- verification checks; and
- automated regression testing.

The AI explanation layer is not the sole decision mechanism.

The tactical decision framework and feasibility logic remain separate from the generative AI component.

## Technology

Current technologies include:

- Python
- FastAPI
- PostgreSQL
- Railway
- Docker
- Alembic
- Pytest
- AI / LLM integration

## Practitioner-Informed Development

Practitioner feedback is used to challenge assumptions in the decision framework.

Where feedback exposes a general weakness, I treat it as a technical question rather than changing the system simply to match one person's preferred tactical answer.

Changes are tested through controlled scenarios and regression testing before deployment.

## Founder Contribution

Football Decision Intelligence was conceived, designed, developed, tested and deployed by Adebayo Oyeleye.

My work has included:

- product concept and architecture;
- tactical decision workflow;
- feasibility and constraint logic;
- scoring methodology;
- AI explanation and verification;
- automated testing;
- deployment;
- practitioner validation; and
- product calibration.

The core product has not been outsourced.

## Product Boundaries

FDI does not currently claim to:

- replace a football coach;
- provide objectively correct tactical decisions;
- predict match outcomes;
- provide validated win probabilities;
- replace video analysis; or
- replace player-tracking systems.

The current outputs are decision-support signals intended to help coaches compare realistic options.

## Commercial Status

FDI is currently in private beta and remains pre-revenue.

Practitioner validation and commercial testing are ongoing.

The next commercial stage is focused on willingness to pay, paid pilots, repeat usage and recurring subscriptions.