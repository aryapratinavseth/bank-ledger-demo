# bank-ledger-demo

A small, self-contained bank ledger (accounts, transfers, interest, fees, statements) used to
demonstrate [Lexsi Mason](https://lexsi.ai), a coding agent, on realistic banking code.

The code is deliberately small and has a few open issues, so each demo is short and checkable:
fix a bug from an issue, implement a feature, review for security, and carry a longer change
across sessions.

## Run the tests

```bash
python -m pip install pytest
python -m pytest -q
```

## Layout

| Path | What it is |
|---|---|
| `src/ledger/accounts.py` | Accounts, deposits, idempotent transfers |
| `src/ledger/interest.py` | Savings interest (policy in `docs/policy.md`) |
| `src/ledger/fees.py` | Fee schedule read from the bank's fee configuration |
| `src/ledger/statements.py` | Plain-text statements |
| `tests/` | pytest suite |
| `docs/policy.md` | The business rules the code must follow |
| `AGENTS.md` | Rules for coding agents working in this repository |

**Demo code, not for production use.** It contains deliberate defects, including one security flaw,
for the agent to find and fix on camera. Synthetic data only.
