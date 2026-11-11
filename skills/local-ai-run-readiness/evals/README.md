# Evaluation cases

`evals.json` defines seven synthetic prompts, expected outcomes and review expectations. These are test specifications, not records of completed model evaluations.

An authorized evaluator should give the candidate skill and one prompt to an assistant, preserve the returned answer and check every expectation. Record failures and abstentions as well as successful behavior. Compare against the same task without the candidate when assessing improvement. Do not manufacture scores from the presence of this file.

No case requires a real model load on the operator's machine, private documents, network access or paid APIs. No evaluation runs are bundled. The positive case prevents a refusal-only workflow from appearing successful merely because it blocks every task.
