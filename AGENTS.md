# Rules for coding agents

- Money is `decimal.Decimal`, never `float`. Round to the cent with `ROUND_HALF_UP` unless `docs/policy.md` says otherwise.
- Every behaviour change comes with a test. Run `python -m pytest -q` before you say a task is done.
- Follow `docs/policy.md`; if the code and the policy disagree, the policy wins and the code is the bug.
- Never execute configuration or user input as code.
- Keep changes small: one issue, one branch, one pull request.
