---
name: fde-client-solutioning
description: Use for client-facing or domain-specific solution work in this repo: discovery, mapping business terms to data, prototyping a solution, planning deployment, and writing handover notes. Trigger on requests about a client use case, a customer problem, a domain workflow, or a solution demo.
---

# Forward-deployed solutioning

Follow `CLAUDE.md` §9. Use this process.

## 1. Discovery
Write down, in the client folder's README (`clients/<name>/` or `pocs/<name>/`):
- The business problem in one sentence, and who has it.
- Terms, KPIs and their definitions, as the client uses them.
- Systems involved, data owners, and access constraints.
- Assumptions, and the open questions to confirm.

Do not start building until the main assumptions are written down.

## 2. Domain mapping
- Map each business term to a data field, and note any mismatch.
- List the stakeholders and what each one needs to see or decide.

## 3. Prototype
- Build the smallest version that answers the core question, using synthetic or sanitised data.
- Separate the reusable core (`packages/` or the POC's shared module) from the client-specific configuration.
- Make configuration explicit: rules, thresholds and mappings in a config file, not hardcoded.

## 4. Validate with the people who know the domain
- Show results with the assumptions stated.
- Record the feedback and each decision in `memory/TECHNICAL_DECISIONS.md`.

## 5. Deployment and operating model
Document, as proposals unless already tested:
- Where it runs, how it is scheduled, and who is paged on failure.
- Data access, privacy and retention, and what needs approval.
- Cost drivers and their owners.

## 6. Handover
Produce a handover note: purpose, how to run it, configuration, known limitations, risks, and open questions. Label what was tested, what was simulated, and what is only proposed.
