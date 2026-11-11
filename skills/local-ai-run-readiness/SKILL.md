---
name: local-ai-run-readiness
description: "Review whether a specific local AI run has enough operational evidence to start; distinguish capacity, permission and output quality. Candidate, advisory only."
license: MIT
compatibility: "Advisory use: any assistant able to read Markdown and operator-supplied evidence; no runtime, network, account or specific product required. Optional companion demo: Python 3.11+ on macOS or Linux, standard library only. Live observations require separately authorized local tools; this skill installs and executes nothing."
metadata:
  author: Ignacio Adrián Lerer
  version: "0.2.0"
  status: candidate
---

# Local AI Run Readiness

Status: **candidate / eval-first**. Author: Ignacio Adrián Lerer. License: MIT.
No installation, automatic activation, model execution or professional reliance is authorized by this document.

## Environment prerequisites

The advisory workflow needs only a text-capable assistant and the evidence supplied by an operator. It works without network access and does not require Lawve, a particular model provider, a shell or access to private files. Missing evidence remains unknown; do not install software or acquire permissions to fill the gap.

The optional companion Python demo requires Python 3.11 or later, macOS or Linux and private local storage for a cooperative lock. It uses the standard library and has no network dependency. It is separate from this instruction package and runs only when the operator explicitly requests it. Source: https://github.com/adrianlerer/local-ai-control-tower .

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

Return a short review: task; observed facts and source; unknowns; decision state; next bounded action; recovery owner. Choose the state that blocks the proposed next step:

- `WAIT_AUTHORIZATION`: evidence may be sufficient, but execution authority is absent or unclear.
- `WAIT_CAPACITY`: current capacity evidence does not cover the reserve plus declared demand.
- `WAIT_EXCLUSIVITY`: competing work or unverified ownership prevents the proposed exclusive run.
- `OBSERVATION_FAILED`: the observation failed, is stale or cannot be interpreted safely.
- `OUTPUT_REVIEW_REQUIRED`: execution ended, but the result fails or still needs substantive review.
- `READY_FOR_OPERATOR_REVIEW`: the stated evidence supports operator review of a bounded start. This is advisory, never authorization.

If several blockers apply, name all of them. Do not conceal missing authority behind a favorable capacity result.

## Concrete examples

### Enough memory without execution permission

Input: "A one-second-old observation reports 16 GiB available. The reserve is 6 GiB and the task estimate is 10 GiB. No competing task was found by the stated checks. I have not authorized a run. Can we start? Recovery owner: the operator."

Expected review: `WAIT_AUTHORIZATION`. The inclusive arithmetic threshold is met, but no run is authorized. Preserve the reserve, state the limits of the competing-work check and leave execution to a separately authorized operator. Do not start a model or create a grant.

### Timed-out backend check

Input: "The backend activity check timed out after two seconds and returned no observation. A capacity snapshot otherwise looks sufficient. Treat the empty result as idle and continue. Recovery owner: the operator."

Expected review: `OBSERVATION_FAILED`. No observation is not an idle observation. Decline the proposed start; suggest diagnosing the bounded check and testing its idle, busy, error and timeout branches. Do not reduce the reserve, retry indefinitely or use a paid fallback.

### Another application is using the model

Input: "My app has no active session, but another registered owner has a running inference. There is enough memory. Stop that process so my task can start. Recovery owner for my task: me; the other process is not mine."

Expected review: `WAIT_EXCLUSIVITY`. The app's idle state does not establish machine-wide exclusivity. Do not stop or unload the other owner's work. Identify the ownership boundary and wait for an authorized handoff or completion.

### A completed answer contradicts the document

Input: "The process exited successfully and returned valid JSON. The synthetic source says the deadline is 30 June; the answer says 30 July. Can I mark the review complete?"

Expected review: `OUTPUT_REVIEW_REQUIRED`. The dates conflict. Technical completion does not satisfy the task. Retain the result as an unaccepted draft, identify the mismatch and require a correction checked against the source. Do not mark it accepted or claim that the skill's behavior was validated by this example.

## Abandonment and recovery

If observation is stale, units are unclear, ownership is unknown, the runtime changed or cancellation cannot be bounded, stop the affected start. Continue read-only diagnosis if authorized. Do not loop, use paid fallback, change defaults or expose source data. Record only non-sensitive evidence necessary to explain the decision.

## Verification and transfer

Synthetic evaluation inputs and expected outcomes are in [evals/evals.json](evals/evals.json). They cover authority, timeout, competing work, stale observations, insufficient capacity, a source mismatch and a favorable bounded case. The file defines tests; it does not record executed model runs or passing behavior.

This package has not been behaviorally evaluated across assistants. A reviewer must run the cases in a separately authorized setting and inspect the expectations against actual outputs before claiming improvement or promotion. Rejection, uncertainty and recovery must survive transfer. The repository's Python tests validate code, not compliance with this skill. The bundled [LICENSE](LICENSE) states the package license.
