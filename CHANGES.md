# Super77Pro v1.1.0 – Change report (UI/UX redesign, audit and hardening)

Scope: frontend only. No Firebase, backend, payments or admin panel were added. Payout tables, multipliers and probabilities are unchanged (`www/js/rules.js` only gained an additive `wl` field listing winning line indexes).

## Audit summary (before any change)
Stack: static HTML + one stylesheet + 5 JS files (core, rules, slot, wheel, greedy) + Capacitor. Original tests: 128/129 (GreedyBaby tiles overflowed at 320 px). Findings: stylesheet was ~160 lines of stacked overrides (duplicate `:root`, `body`, `.chips`, `.pt`, `.g` rules); emoji used as UI icons; `Impact` font dependency for the 7 symbol; `logo.png` (545 KB) unused by the app; hardcoded "Fortune Hive" in HTML; native `confirm()` for reset; "coming soon" buttons looked live.

## Game-logic bugs found and fixed
1. **Free money on exit (Fruit Wheel and GreedyBaby):** closing the game during the 3–3.5 s result pause refunded bets that had already been paid or lost (reproduced: wheel 5,700 → 5,800 after a ₹100 bet that had already settled). Fix: the round takes ownership of the bets when betting closes. Regression tests added for both games.
2. Corrupt or missing localStorage (`sp_st`, `la_w`) could throw or show NaN; data is now sanitised on load (tested).
3. Layout: GreedyBaby tiles overflowed at 320 px (`minmax(0,1fr)` grid fix).

## Files
- **Modified:** `www/index.html`, `www/js/core.js`, `slot.js`, `wheel.js`, `greedy.js`, `rules.js` (additive), `www/css/style.css` (rewritten), `tests/e2e.py`, `package.json` (version, `test` script), `.gitignore`, `README.md`, `TEST_REPORT.md`.
- **Added:** `www/css/games.css`, `www/js/sprite.js`, `tests/check_project.py`, `docs/INTEGRATION_NOTES.md`, `CHANGES.md`.
- **Removed:** `www/assets/logo.png` (545 KB, referenced by nothing in HTML/CSS/JS; README mention updated). The Android icon/splash sources in `assets/` were kept as-is (already losslessly optimal; icon-only/icon-foreground and splash/splash-dark are byte-identical copies but both names are used by `@capacitor/assets`). Web bundle: 287 KB.

## CSS / design system
Single token set (colors, radii, spacing, type, shadows, tap size, motion) in `style.css`, organised in 9 numbered sections; per-game styling separated in `games.css`. Navy/charcoal base, emerald and gold accents, no always-on glows. Safe-area insets, `100dvh`, reduced-motion support, focus-visible rings, 40–48 px touch targets.

## Screens
- **Home:** compact header (brand, guest ID, "Test balance" chip), test-mode banner, three game cards with tag/title/Play, Earn zone clearly marked *Coming soon* (tap shows a toast), bottom nav with active pill + `aria-current`.
- **Lucky777:** cabinet with marquee, cream reel window, reels stop in sequence with landing bounce, five numbered payline chips that light up on a win plus a coloured line drawn *behind* the symbols, ringed winning cells, Paytable dialog (symbols, five payline diagrams, worked example), −/＋ bet stepper with total bet and per-line bet, AUTO, large SPIN; controls disabled while spinning; insufficient-balance message with shake.
- **Super77Pro wheel:** vector wheel (SVG) coloured by symbol (melon red, mango amber, 77 violet), lit rim, hub countdown, timer bar, gold pointer, winning wedge highlight; bet boxes coloured to match; chip + total-bet readouts; casino-style chips with clear selected state; results strip with newest highlighted. Final rotation verified to match the reported section.
- **GreedyBaby:** warm wooden board with cream tiles, tiered multiplier pills, bet badges, running light, WIN ribbon, centre countdown/result, chip + total-bet readouts.
- **Wallet:** virtual-balance card ("not real money, cannot be withdrawn"), bets/wagered/won/net tiles, history rows with Bet / Win / Refund / Test credit labels, sign, icon and balance-after, empty state.
- **Profile:** player card, sound switch, Reset test data behind an in-app confirmation dialog with success toast, About/disclaimer.
- **Shared:** dialogs (Esc / ✕ / backdrop / focus trap), toasts, Android back button closes game/panel/dialog via history entries, SVG icons replace emoji UI glyphs, font-independent 7 symbol.

## Performance
Bundle 287 KB (was ~785 KB); no external requests; twinkle/bulb animations run only while a round is spinning; timer bar uses `transform`; reel spin uses `transform`/`opacity` only.
