"""Martingale strategy implementation.

Implements a class with the same API as ParoliStrategy so both can be
swapped easily in `brr.py`.
"""

class MartingaleStrategy:
    """Martingale (negative progression) strategy.

    After a loss, the stake is multiplied (usually doubled) to try to recover
    previous losses. On a win the stake is reset to base_bet.
    """
    def __init__(self, base_bet, multiplier=2):
        self.base_bet = base_bet
        self.multiplier = multiplier
        self.current_bet = base_bet

    def record_result(self, result, placed_bet, balance_after):
        """Return the next bet given the last result.

        result: 'win' or 'loss'
        placed_bet: the amount that was just wagered
        balance_after: balance available for the next bet
        """
        if result == "loss":
            next_bet = placed_bet * self.multiplier
            # if the next bet would exceed current balance, either go all-in or return 0
            if next_bet >= balance_after:
                if balance_after == 0:
                    self.current_bet = 0
                    return 0
                self.current_bet = balance_after
                return balance_after

            self.current_bet = next_bet
            return next_bet

        # on win: reset to base bet
        self.current_bet = self.base_bet
        return self.base_bet
