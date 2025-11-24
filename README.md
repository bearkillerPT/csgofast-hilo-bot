## CSGOFast bot

- Install Playwright:

```powershell
pip3 install playwright
## Quick README

- Install Playwright:

```powershell
pip3 install playwright
playwright install
```

- Optional env (choose strategy):

```powershell
# $env:BET_STRATEGY = "paroli"    # or "martingale" (default: paroli)
```

- Run the bot:

```powershell
python farm_hilo.py
```

- First run: log in to csgofast and open the Free Coins tab. Later runs reuse `my_profile` so the bot should find you logged in and you just need to click the Free Coins tab to start.

- What the bot does:
  1. Clicks Free Coins to claim the 100 free coins (even if you still have a positive balance).
  2. Opens the HiLo game and bets on red repeatedly while balance > 0.
  3. When balance reaches 0 it will try to claim free coins again and continue.

- Strategies (in `strategies/`):
  - Martingale — double after a loss, reset on win.
  - Paroli — increase after wins up to a target streak, then reset.

That's all. Keep it minimal.

Note: see `.env` for example parameters for each strategy.