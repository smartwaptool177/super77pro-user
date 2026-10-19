# Firebase plan (next phase)
/users/{uid}/profile (client writes own), /wallet and /tx (written only by Cloud Functions, never by the client),
/results/{round} (server-generated with a secure RNG), /settings (admin only, custom claim admin=true).
Bets, results and payouts must be computed in Cloud Functions; the app only sends a bet request and shows the response.
