# Super77Pro

Mobile-first game app (Capacitor + plain HTML/CSS/JS, no framework): **Lucky777** slots, **Super77Pro** fruit wheel, **GreedyBaby** food game, plus Wallet and Profile.

**Status: test mode (v1.1.0).** All coins are virtual. Balances and results are generated on the device and stored in `localStorage`, which is fine for a demo but must never be used to secure real money. Firebase, server-side results, payments and the admin panel are the next phase (see `docs/INTEGRATION_NOTES.md`).

## Run / test / build
- Preview: open `www/index.html` in a browser (works from `file://`, fully offline, no network requests).
- Static checks: `python3 tests/check_project.py .`
- Browser tests: `python3 tests/e2e.py .` (Python + Playwright + Chromium). Results: `TEST_REPORT.md`.
- APK: push to GitHub → Actions → *Build APK* → Run workflow → download `super77pro-apk`. Locally:
  `npm install && npx cap add android && npx @capacitor/assets generate --android && npx cap sync android && cd android && ./gradlew assembleDebug`
  → `android/app/build/outputs/apk/debug/app-debug.apk`

## Structure
```
www/index.html        app shell (home, game screen, wallet/profile panel, dialog, toast)
www/css/style.css     design system tokens + shared UI (home, nav, panels, dialogs)
www/css/games.css     per-game styling (Lucky777, wheel, GreedyBaby)
www/js/sprite.js      inline SVG sprite: game symbols, nav and UI icons
www/js/core.js        helpers, wallet, state/localStorage, navigation, dialogs, Wallet + Profile
www/js/rules.js       payout rules: single source of truth (tested for RTP)
www/js/slot.js wheel.js greedy.js   the three games
www/js/firebase-config.js           placeholder, not loaded yet
www/assets/           game art (webp) + in-app logo
assets/               Android launcher icon + splash sources (used by @capacitor/assets)
tests/                e2e.py (browser), check_project.py (static)
```
Payout rules live only in `www/js/rules.js`. The in-game paytable/rules dialogs are generated from it, so they cannot drift from the real payouts.
