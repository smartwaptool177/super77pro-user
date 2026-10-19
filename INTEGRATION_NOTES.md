# Next-phase integration notes (nothing here is implemented yet)

Keep the UI; replace the local, trusted-client pieces with server calls.

| Today (local) | Where | Next phase |
|---|---|---|
| Wallet balance `wallet`, `setW()`, key `la_w` | `core.js` | Read-only mirror of the server balance; never written by the client |
| Transactions `txn()`, `ST.tx`, key `sp_st` | `core.js` | Server-written ledger (`/users/{uid}/tx`); Wallet panel (`txRow`, `panel('wallet')`) only renders it |
| Bet deduction (`setW` + `txn('Bet')`) in `slot.js`, `wheel.js`, `greedy.js` | each game | Send a bet request to a Cloud Function; update the UI from its response |
| Result generation `pickW()` / `rnd()` / `RNG` | each game | Server-side secure RNG; client only animates the returned result (reel grid / wheel index / food index) |
| Payout `RULES.*.pay()` | `rules.js` | Same rules computed server-side; keep this file for display + tests |
| Round timers (`round()` countdowns) | wheel, greedy | Shared server round clock (`/results/{round}`) |
| Player ID `ST.id` | `core.js` | Firebase Auth uid |
| Reset test data, "Add ₹1,000" buttons (`addCredit`, `#rs`) | `core.js` | Remove or gate behind an admin/test flag |
| `firebase-config.js` | `www/js` | Paste web config and load the SDK before `core.js` |

Database layout and security rules: see `docs/DATABASE.md` and `database.rules.json`.
