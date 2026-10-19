# Super77Pro – Test Report (v1.1.0)

Automated browser tests (headless Chromium via Playwright, mobile emulation): **160/160 passed**.  
Static project checks (`tests/check_project.py`): **66/66 passed**.

Original v1.0 baseline, run before any change: 128/129 (failure: GreedyBaby tiles overflowed the screen at 320 px width – fixed).

## How to re-run
```
python3 tests/check_project.py .   # references, JS syntax, JSON, sprite ids, assets
python3 tests/e2e.py .             # needs Python + Playwright + Chromium; screenshots go to tests/out/
```

## Result by area

| Area | Checks | Passed |
|---|---|---|
| Slot math | 4 | 4 |
| Wheel math | 8 | 8 |
| GreedyBaby math | 10 | 10 |
| Slot UI | 26 | 26 |
| Wheel UI | 30 | 30 |
| GreedyBaby UI | 35 | 35 |
| Wallet | 9 | 9 |
| Navigation | 12 | 12 |
| Sound | 3 | 3 |
| Profile | 4 | 4 |
| Regression | 3 | 3 |
| Dialog | 3 | 3 |
| Robustness | 2 | 2 |
| Accessibility | 2 | 2 |
| Layout | 8 | 8 |
| Errors | 1 | 1 |

## Automated vs manual
- **Automated:** everything listed below (logic, payouts, wallet, navigation, dialogs, layout bounds at 8 viewport sizes, JS errors).
- **Manual visual inspection (by screenshot, desktop Chromium emulating phones):** Home, all three games (idle, spinning, win, error states), Wallet, Profile, Reset dialog, Paytable dialog at 320, 360, 430 px. Spot-checked, not pixel-diffed.
- **Not performed:** any real Android device or emulator test, APK build, Android WebView run, hardware back-button test (browser history back was tested instead), on-screen-keyboard test (the app has no text inputs), screen-reader test.

## Known issues / limits
- APK could not be built here: the sandbox cannot reach the npm registry (`ENOTFOUND registry.npmjs.org`), so Capacitor and the Android SDK cannot be installed. The GitHub Actions workflow is unchanged; build there.
- The wheel and slot animations are CSS/JS timers; they were verified for correctness (final rotation matches reported section) but not profiled for frame rate on a real phone.
- `Bets placed` counter is not decremented by refunds (wagered total is).
- Results and balance are generated on the device and stored in localStorage: fine for this test phase, **not** suitable for real money.

## Every check

### Slot math
- [x] exact RTP between 93% and 96%
- [x] simulated RTP (1,000,000 spins) within 5 points of exact
- [x] pay() equals independent reference on 3,000 random grids
- [x] all-77 grid pays 200 x bet on 5 lines

### Wheel math
- [x] melon box RTP = 88.9% (<=100%)
- [x] 77 box RTP = 88.9% (<=100%)
- [x] mango box RTP = 88.9% (<=100%)
- [x] all 3 boxes have the same RTP
- [x] pay 🍉 with 10/10/10 = 20
- [x] pay 7️⃣ with 10/10/10 = 80
- [x] pay 🥭 with 10/10/10 = 20
- [x] 77 x8 on 100 pays 800

### GreedyBaby math
- [x] 🍎 x5 RTP 97.2% (<=100%)
- [x] 🍋 x5 RTP 97.2% (<=100%)
- [x] 🍓 x5 RTP 97.2% (<=100%)
- [x] 🥭 x5 RTP 97.2% (<=100%)
- [x] 🐟 x10 RTP 97.2% (<=100%)
- [x] 🍔 x15 RTP 97.2% (<=100%)
- [x] 🍕 x25 RTP 97.2% (<=100%)
- [x] 🍗 x45 RTP 97.2% (<=100%)
- [x] sampled frequencies match weights (±0.6 pt)
- [x] pay = bet x multiplier for all 8 foods

### Slot UI
- [x] BET − stops at 5
- [x] BET + stops at 1,000
- [x] bet steps 1,000 > 500 > 100 > 50 > 10 > 5
- [x] spin grid [[0, 0, 0], [0, 0, 0], [0, 0, 0]] -> wallet change +1990
- [x] spin grid [[6, 6, 6], [0, 1, 2], [3, 4, 5]] -> wallet change -10
- [x] spin grid [[3, 6, 4], [6, 6, 3], [3, 4, 6]] -> wallet change -10
- [x] spin grid [[4, 1, 1], [6, 4, 3], [5, 4, 6]] -> wallet change -10
- [x] spin grid [[1, 0, 3], [2, 1, 0], [4, 6, 5]] -> wallet change -10
- [x] spin grid [[5, 0, 4], [3, 3, 5], [5, 4, 5]] -> wallet change -10
- [x] spin grid [[1, 4, 0], [6, 4, 0], [0, 0, 1]] -> wallet change -10
- [x] spin grid [[1, 4, 0], [6, 3, 2], [3, 4, 6]] -> wallet change -10
- [x] spin grid [[1, 4, 1], [5, 2, 3], [0, 5, 0]] -> wallet change -10
- [x] spin grid [[3, 5, 2], [3, 4, 6], [0, 5, 2]] -> wallet change -10
- [x] spin grid [[2, 6, 1], [4, 2, 0], [0, 4, 6]] -> wallet change -10
- [x] spin grid [[0, 3, 0], [6, 2, 3], [0, 0, 6]] -> wallet change -10
- [x] spin grid [[2, 5, 6], [2, 3, 6], [2, 4, 6]] -> wallet change +146
- [x] reels show 3x3 SVG symbols
- [x] insufficient balance blocks spin
- [x] AUTO spins repeatedly
- [x] AUTO stops by itself when balance too low
- [x] closing mid-spin still settles the result (77 grid)
- [x] triple tap on SPIN deducts the bet only once
- [x] SPIN and bet buttons are disabled while spinning
- [x] controls re-enabled after the spin
- [x] winning payline is lit and drawn (1 line)
- [x] winning cells highlighted (3)

### Wheel UI
- [x] watermelon: 3 bets of 10 deduct 30
- [x] watermelon: box labels show 10
- [x] watermelon: betting blocked while spinning
- [x] watermelon: payout +20
- [x] watermelon: result history shows latest
- [x] watermelon: winning box highlighted
- [x] next round starts: round 2, bets reset, timer back to 10
- [x] countdown ticks down one second at a time
- [x] insufficient balance blocks bet
- [x] closing during bet time refunds the bet
- [x] closing mid-spin settles the result (win paid)
- [x] 77: 3 bets of 10 deduct 30
- [x] 77: box labels show 10
- [x] 77: betting blocked while spinning
- [x] 77: payout +80
- [x] 77: result history shows latest
- [x] 77: winning box highlighted
- [x] mango: 3 bets of 10 deduct 30
- [x] mango: box labels show 10
- [x] mango: betting blocked while spinning
- [x] mango: payout +20
- [x] mango: result history shows latest
- [x] mango: winning box highlighted
- [x] 🍉: wheel stops with the winning section under the pointer
- [x] 🍉: highlighted wedge is the reported one
- [x] 🥭: wheel stops with the winning section under the pointer
- [x] 🥭: highlighted wedge is the reported one
- [x] 7️⃣: wheel stops with the winning section under the pointer
- [x] 7️⃣: highlighted wedge is the reported one
- [x] total bet readout = 150 and chip readout = 50

### GreedyBaby UI
- [x] countdown ticks down
- [x] round 1: 8 bets of 10 deduct 80
- [x] round 1: betting blocked while drawing
- [x] round 1: winner 🍎 x5 pays 50
- [x] round 1: history newest first
- [x] round 2: 8 bets of 10 deduct 80
- [x] round 2: betting blocked while drawing
- [x] round 2: winner 🍋 x5 pays 50
- [x] round 2: history newest first
- [x] round 3: 8 bets of 10 deduct 80
- [x] round 3: winner 🍓 x5 pays 50
- [x] round 3: history newest first
- [x] round 4: 8 bets of 10 deduct 80
- [x] round 4: winner 🥭 x5 pays 50
- [x] round 4: history newest first
- [x] round 5: 8 bets of 10 deduct 80
- [x] round 5: winner 🐟 x10 pays 100
- [x] round 5: history newest first
- [x] round 6: 8 bets of 10 deduct 80
- [x] round 6: winner 🍔 x15 pays 150
- [x] round 6: history newest first
- [x] round 7: 8 bets of 10 deduct 80
- [x] round 7: winner 🍕 x25 pays 250
- [x] round 7: history newest first
- [x] round 8: 8 bets of 10 deduct 80
- [x] round 8: winner 🍗 x45 pays 450
- [x] round 8: history newest first
- [x] round 9: 8 bets of 10 deduct 80
- [x] round 9: winner 🍎 x5 pays 50
- [x] round 9: history newest first
- [x] history capped at 8 items
- [x] insufficient balance blocks bet
- [x] closing during bet time refunds
- [x] closing mid-draw settles (fish x10 pays 100)
- [x] total bet readout = 200

### Wallet
- [x] + adds test balance ₹1,000
- [x] balance = 5000 + credits − wagered + won
- [x] bets placed counter
- [x] balance saved after reload
- [x] history and totals saved after reload
- [x] history rows shown
- [x] Today's win saved after reload (slot)
- [x] wheel history saved after reload
- [x] empty state message

### Navigation
- [x] tab wallet: exactly one active
- [x] tab wallet: panel state
- [x] tab profile: exactly one active
- [x] tab profile: panel state
- [x] tab games: exactly one active
- [x] tab games: panel state
- [x] tab home: exactly one active
- [x] tab home: panel state
- [x] browser/Android back closes an open game
- [x] back closes the Wallet panel and Home tab is active
- [x] open/close/open quickly keeps the new game open (no stale back event)
- [x] 24 rapid tab switches + game open/close: always exactly one active tab

### Sound
- [x] header button toggles sound
- [x] profile toggle off
- [x] setting saved after reload

### Profile
- [x] reset test data restores ₹5,000 and clears history
- [x] reset asks for confirmation (dialog shown)
- [x] Cancel keeps balance and history
- [x] Confirm resets and shows success toast

### Regression
- [x] wheel: closing during the result pause does not refund settled bets
- [x] greedy: closing during the result pause does not refund settled bets
- [x] wheel: two bets then close refunds exactly the two bets once

### Dialog
- [x] paytable dialog opens with 7 symbols and 5 payline diagrams
- [x] Escape closes the dialog
- [x] info button + X close work

### Robustness
- [x] corrupt saved data does not crash: balance falls back to 5000, panels and games still open
- [x] negative saved balance is rejected

### Accessibility
- [x] chips, header buttons and bet boxes are at least 40px touch targets
- [x] game status message is a polite live region

### Layout
- [x] 320x568: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)
- [x] 360x640: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)
- [x] 375x667: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)
- [x] 390x844: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)
- [x] 412x915: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)
- [x] 430x932: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)
- [x] 768x1024: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)
- [x] 640x360: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)

### Errors
- [x] no JavaScript errors in the whole run
