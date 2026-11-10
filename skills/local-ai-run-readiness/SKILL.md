---
name: local-ai-run-readiness
description: "Review whether a specific local AI run has enough operational evidence to start; distinguish capacity, permission and output quality. Candidate, advisory only."
---

# Local AI Run Readiness

Status: **candidate / eval-first**. Author: Ignacio Adrián Lerer. License: MIT.
No installation, automatic activation, model execution or professional reliance is authorized by this document.

## Trigger and exclusions

Use when an operator asks whether a specified local model task can start or why a local run was rejected. Do not use as a general writing skill, a legal verifier, a resource allocator or an instruction to stop another person's work.

## Required input

Task and intended output; runtime/model identifiers; known context and output bounds; evidence of current capacity with units, method and timestamp; configured reserve; observed competing work; execution authority; time limit and recovery owner. Do not request secret values, document bodies or full process command lines.

## Procedure

1. Separate three questions: capacity, authorization and task success. A favorable estimate answers only the first, and only within its observed scope.
2. Check bytes versus GiB, inclusive threshold, freshness, observer failures and the meaning of available memory. Do not infer inference demand from download size.
3. Check whether all participants cooperate with the same exclusion mechanism. No active work found in one app does not prove the machine is idle.
4. Identify the exact reason for refusal. Timeout means observation failed, not that the backend is idle. Preserve the configured reserve; do not lower it, unload models or kill processes to manufacture admission.
5. If a control is defective, propose the smallest correction and tests for free, busy, error and timeout cases. A measured, bounded observation may replace a defective one; removing the check requires a separate decision.
6. Before execution, require an existing authorized executor and recovery path. This skill cannot issue grants or treat its own recommendation as permission.
7. After a real run, check complete output and then semantic quality against the task. Do not accept valid JSON, process exit or model agreement as proof of quality. Restore only resources owned by that run.

## Output

Return a short review: task; observed facts and source; unknowns; `READY_FOR_OPERATOR_REVIEW`, `WAIT_CAPACITY`, `WAIT_EXCLUSIVITY` or `OBSERVATION_FAILED`; next bounded action; recovery owner. `READY_FOR_OPERATOR_REVIEW` is advisory, never authorization.

## Abandonment and recovery

If observation is stale, units are unclear, ownership is unknown, the runtime changed or cancellation cannot be bounded, stop the affected start. Continue read-only diagnosis if authorized. Do not loop, use paid fallback, change defaults or expose source data. Record only non-sensitive evidence necessary to explain the decision.

## Verification and transfer

This package has not been behaviorally evaluated across assistants. A reviewer should test at least: enough memory but no permission; timeout with no output; foreign active work; stale favorable snapshot; a completed but semantically wrong result. Rejection, uncertainty and recovery must survive transfer. The repository's Python tests validate code, not compliance with this skill.
