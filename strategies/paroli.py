"""Paroli strategy implementation.

Paroli is a positive progression: increase the stake after wins up to a
target streak, then reset (bank profits). API mirrors MartingaleStrategy.
"""

class ParoliStrategy:
    def __init__(self, base_bet, multiplier=2, target_streak=3):
        self.base_bet = base_bet
        self.multiplier = multiplier
        self.target_streak = target_streak
        self.win_streak = 0
        self.current_bet = base_bet

    def record_result(self, result, placed_bet, balance_after):
        """Update internal state and return next bet amount.

        result: 'win' or 'loss'
        placed_bet: the amount that was just wagered
        balance_after: balance available for the next bet
        """
        if result == "win":
            self.win_streak += 1
            # If we've reached the target streak, reset after this win (bank profits)
            if self.win_streak >= self.target_streak:
                next_bet = self.base_bet
                self.win_streak = 0
                self.current_bet = self.base_bet
                return next_bet

            # Otherwise increase the bet by multiplier but don't exceed balance
            next_bet = placed_bet * self.multiplier
            if next_bet >= balance_after:
                if balance_after == 0:
                    self.current_bet = 0
                    self.win_streak = 0
                    return 0
                self.current_bet = balance_after
                return balance_after

            self.current_bet = next_bet
            return next_bet

        # on loss: reset and clear streak
        self.win_streak = 0
        self.current_bet = self.base_bet
        return self.base_bet
