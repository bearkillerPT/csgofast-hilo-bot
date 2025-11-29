from os import path, environ, makedirs
from time import sleep
from datetime import datetime
from playwright.sync_api import sync_playwright
from logger import FileLogger, get_latest_tickets_iso_date
from config import EnvConfig
from farm_ticktes import collect_tickets_routine

free_coins_btn = ".valve-btn"
hilo_value_input = ".app_input"
current_money_span = ".free-coins"
bet_red_btn = ".colorRed"
countdown_timer_span = ".progress-bar__container"
app_button = ".app_button"

# initialize logger (file will be created in the project folder)
# Prepare logs directory and strategy-specific filename
# Use a local logs/ folder inside the project (next to this file)
project_root = path.dirname(path.abspath(__file__))
logs_dir = path.join(project_root, "logs")
makedirs(logs_dir, exist_ok=True)

# Load configuration (this will read .env if present) and build the strategy
cfg = EnvConfig(project_root)
strategy_name = cfg.strategy_name
log_file = path.join(logs_dir, f"{strategy_name}_game_logs.csv")

logger = FileLogger(log_file)

# Use configured base bet from env (falls back to 25 if not set)
default_bet_amount = cfg.base_bet

# Instantiate the configured strategy (use default_bet as fallback)
strategy = cfg.get_strategy(default_bet_amount)


def get_current_money(page):
    page.wait_for_selector(current_money_span)
    money_text = page.query_selector(current_money_span).inner_text()
    money_value = float(money_text.replace(",", ".").replace(' ','').replace('\n',''))
    return money_value

def get_countdown_timer(page):
    countdown = page.query_selector(countdown_timer_span)
    if countdown is None:
        return None
    return countdown.inner_text()
    
def collect_rewards(page):
    page.goto("https://csgofast.com/free-coins")
    page.wait_for_timeout(2500)
    free_coins = page.wait_for_selector(free_coins_btn)
    free_coins.click()

    # log that we attempted to collect free coins
    logger.log_event("collect_rewards", details=f"clicked free coins; balance={get_current_money(page)}")

def load_hilo_page(page):
    page.goto("https://csgofast.com/free-coins/hilo")
    page.wait_for_selector(hilo_value_input)

def play_hilo(page):
    load_hilo_page(page)
    hilo_input = page.query_selector(hilo_value_input)
    current_money = get_current_money(page)
    last_money = current_money
    current_bet = default_bet_amount if current_money > default_bet_amount else current_money
        
    while current_money > 0:
        collect_tickets_routine(page)
        
        if page.url != "https://csgofast.com/free-coins/hilo":
            load_hilo_page(page)
            hilo_input = page.query_selector(hilo_value_input)
            page.wait_for_timeout(1000)
         
        page.wait_for_selector(countdown_timer_span)
        # place the current bet
        placed_bet = current_bet
        print(f"Current Money: {current_money}, Placed Bet: {placed_bet}")
        
        if current_bet == current_money or current_bet >= 500:
            # select all app_buttons and click on the one with " All " written on it
            buttons = page.query_selector_all(app_button)
            for button in buttons:
                if "All" in button.inner_text():
                    try:
                        button.click()
                    except Exception as e:
                        print(f"Error clicking 'All' button: {e}")
                        return
            
        else:
            try:
                hilo_input.fill(str(placed_bet))
            except Exception as e:
                print(f"Error filling hilo input: {e}")
                return
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
        
        # Don't try to repeatedly bet 500 if the max iterations are reached
        if next_bet > 500:
            next_bet = default_bet_amount
        
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
    
    while True:
        collect_rewards(page)
        play_hilo(page)
        page.wait_for_timeout(1000)
