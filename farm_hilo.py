from os import path, environ, makedirs
from time import sleep
from playwright.sync_api import sync_playwright
from logger import FileLogger
from strategies.paroli import ParoliStrategy
from strategies.martingale import MartingaleStrategy

free_coins_btn = ".valve-btn"
hilo_value_input = ".app_input"
current_money_span = ".free-coins"
bet_red_btn = ".colorRed"
countdown_timer_span = ".progress-bar__container"
default_bet_amount = 25

# initialize logger (file will be created in the project folder)
# Choose strategy: 'paroli' or 'martingale' (case-insensitive)
STRATEGY = environ.get("BET_STRATEGY", "paroli").lower()

# Prepare logs directory and strategy-specific filename
# Use a local logs/ folder inside the project (next to this file)
project_root = path.dirname(path.abspath(__file__))
logs_dir = path.join(project_root, "logs")
makedirs(logs_dir, exist_ok=True)

if STRATEGY == "martingale":
    log_file = path.join(logs_dir, "martingale_game_logs.csv")
else:
    # default to Paroli
    log_file = path.join(logs_dir, "paroli_game_logs.csv")

logger = FileLogger(log_file)


def get_current_money(page):
    page.wait_for_selector(current_money_span)
    money_text = page.query_selector(current_money_span).inner_text()
    money_value = float(money_text.replace(",", ".").replace('\n',''))
    print(f"Current Money: {money_value}")
    return money_value

def get_countdown_timer(page):
    countdown = page.query_selector(countdown_timer_span)
    if countdown is None:
        return None
    return countdown.inner_text()
    
def collect_rewards(page):
    page.goto("https://csgofast.com/free-coins")
    free_coins = page.wait_for_selector(free_coins_btn)
    free_coins.click()
    # log that we attempted to collect free coins
    try:
        current = get_current_money(page)
    except Exception:
        current = None
    logger.log_event("collect_rewards", details=f"clicked free coins; balance={current}")

def play_hilo(page):
    page.goto("https://csgofast.com/free-coins/hilo")
    page.wait_for_selector(hilo_value_input)
    hilo_input = page.query_selector(hilo_value_input)
    current_bet = default_bet_amount
    last_money = get_current_money(page)

    # choose strategy based on BET_STRATEGY env var
    if STRATEGY == "martingale":
        strategy = MartingaleStrategy(base_bet=default_bet_amount, multiplier=2)
    else:
        strategy = ParoliStrategy(base_bet=default_bet_amount, multiplier=2, target_streak=3)

    while get_current_money(page) > 0:
        page.wait_for_selector(countdown_timer_span)
        # place the current bet
        placed_bet = current_bet
        hilo_input.fill(str(placed_bet))
        red_btn = page.query_selector(bet_red_btn)
        red_btn.click()

        # wait for the timer to reach 00:00
        while get_countdown_timer(page) != "00:01":
            sleep(.1)
        while get_countdown_timer(page) is None:
            sleep(.1)
        while get_countdown_timer(page) != "00:10":
            sleep(.1)

        current_money = get_current_money(page)
        # determine result
        if current_money < last_money:
            result = "loss"
        else:
            result = "win"

        # ask the chosen strategy for the next bet
        next_bet = strategy.record_result(result, placed_bet, current_money)

        # log the resolved bet (log the bet we placed, not the next bet)
        logger.log_bet(placed_bet, result, balance_before=last_money, balance_after=current_money)

        # set up for next round
        current_bet = next_bet
        last_money = current_money
        
        
        
        


with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="my_profile",
        headless=False,
    )
    page = browser.new_page()
    page.goto("https://csgofast.com")
    page.wait_for_timeout(2000)
    page.wait_for_url("https://csgofast.com/free-coins")
    
    # your repeated actions
    while True:
        # Login and go to the free coins page
        collect_rewards(page)
        play_hilo(page)
