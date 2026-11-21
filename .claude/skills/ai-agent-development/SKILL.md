---
name: ai-agent-development
description: Use when designing or building an AI agent, LLM application, tool-calling workflow or MCP server in this repo. Covers scope and tool definitions, least-privilege permissions, approval gates for write actions, timeouts and retries, structured output, tracing, and agent evaluations such as prompt-injection and unauthorised-tool tests.
---

# AI agent development

Follow `CLAUDE.md` §6. Use this checklist when building.

## 1. Decide whether an agent is needed
- If the steps are known in advance, write a deterministic pipeline. Use an agent only where the model has to choose the next step.
- Write one paragraph: purpose, inputs, outputs, and what the agent must never do.

## 2. Define the tools
- Each tool gets a typed schema (input and output) and a docstring that says when to use it.
- Mark each tool **read** or **write**. Write tools need an explicit human approval step before they run.
- Give the agent only the tools it needs (least privilege).

## 3. Separate the layers
- Prompts in their own files.
- Tool implementations in their own module, with no LLM calls inside them.
- Business rules in plain code that can be tested without a model.
- Evaluation cases in their own folder.

## 4. Control the loop
- Set a maximum number of tool calls per run, a timeout per call, and a bounded retry count with backoff.
- On failure, degrade gracefully and return the error to the caller. Do not loop.
- Validate the model's output against the schema before passing it to any other system.

## 5. Trace
- Log each model call and tool call with inputs, outputs, latency and errors. Redact secrets and personal data.

## 6. Evaluate before calling it done
Run these and record the actual results in `docs/VALIDATION.md`:
- Tool selection: does it pick the right tool for each test prompt?
- Schema compliance: does every tool call match its schema? Test with malformed arguments.
- Prompt injection: feed instructions hidden in retrieved text or tool output. The agent must not follow them.
- Unauthorised tools: a request for a write action without approval must not execute it.
- Failure paths: timeouts, empty tool results, and conflicting context.
- Grounding: answers must cite the evidence they used, or say that the evidence is missing.

## 7. Limitations
Document the known failure modes, and say which evaluations were not run and why.
