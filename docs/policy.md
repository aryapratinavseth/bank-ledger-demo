# Ledger policy

1. **Money.** Amounts are held to two decimal places in the account's currency.
2. **Interest.** Simple daily interest on the closing balance, actual/365, rounded to the cent, half up.
   Example: 2,675.00 at 3.65% for 10 days is 2.675, which rounds to **2.68**.
3. **Transfers.** Same currency only. A retried transfer with the same reference must not move money twice.
   An account may not go below zero.
4. **Daily limit.** (Planned, issue #2.) Outgoing transfers per account per calendar day are capped,
   default 1,00,000.00, configurable per account.
5. **Fees.** Fee rules come from configuration as simple arithmetic in `amount`
   (numbers, `+ - * /`, `min`, `max`). Configuration is data, not code.
