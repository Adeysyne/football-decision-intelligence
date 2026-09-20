# Project 5 checkpoint
Updated: 20 September 2026

## Product and purpose
Football Decision Intelligence: low-data tactical decision
support for coaches, developed towards paying customers,
repeat usage and independent income.

Project 6 trading is separate.

## Verified progress
- Scenario intake API implemented.
- Tactical decision engine produces options, scores and rankings.
- AI configuration loads.
- POST /api/v1/ai/analyse is registered.
- Full automated test suite: 35 passed, 1 warning.
- One live sample request returned HTTP 200.
- Model: gpt-5.6-luna.
- Usage: 1517 input tokens, 634 output tokens, 2151 total.
- Live response saved in evidence/live_ai_response.json.

## Current stage
Stage 4: AI reasoning, retrieval and critic/verifier.
Live AI generation works for one sample scenario.
Full live-response quality review remains pending.

## Existing controls
- Engine scores and rankings remain separate from AI prose.
- Schema validation and option-ID matching.
- Numerical-percentage check.
- Controlled provider errors, timeout and disabled SDK retries.

These checks do not establish football accuracy or replace
the planned critic/verifier and grounded retrieval.

## Next work
Review the saved response, then continue Stage 4.
Database, customer UI, authentication, payments, deployment
and external pilots remain upcoming.

## Repository status
Local folder: football-decision-intelligence.
Git previously reported that it was not a repository.
No GitHub remote or commit history has been verified.

## Working preferences
Five-step batches, labelled PowerShell, VS Code or Browser.
Provide complete replacement files and code commands.
Preserve completed work; do not restart or redesign.