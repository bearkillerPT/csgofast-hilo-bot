"""Fractional compounding (Kelly-style) strategy.

This strategy bets a fraction of the current balance each round. It follows the
user specification:

- For small balances (< small_threshold) bet full balance (all-in).
- For medium balances (small_threshold - medium_threshold) bet between
  medium_max_fraction (aggressive at the low end) and medium_fraction (safer at
  the high end of the band).
- For very large balances (> medium_threshold) use a smaller fixed fraction to
  reduce variance.

The class mirrors the API used by other strategies in this project:
  record_result(result, placed_bet, balance_after) -> next_bet

This implementation does not try to estimate p or compute classical Kelly
exactly; it implements a practical fractional compounding approach guided by
the user's tiers and configurable parameters.
"""

class FractionalStrategy:
    def __init__(
        self,
        min_bet=1,
        max_bet=None,
        small_threshold=500,
        medium_threshold=5000,
        small_fraction=1.0,
        medium_fraction=0.5,
        medium_max_fraction=0.75,
        high_fraction=0.25,
    ):
        """Create a FractionalStrategy.

        Parameters:
        - min_bet: minimum bet size (will be enforced unless balance is smaller)
        - max_bet: optional absolute cap on bet size
        - small_threshold: balances strictly below this are treated as "small"
        - medium_threshold: upper bound for the medium band
        - small_fraction: fraction to wager when balance < small_threshold (default 100%)
        - medium_fraction: baseline fraction used near medium_threshold (default 50%)
        - medium_max_fraction: fraction used at the low end of medium band (default 75%)
        - high_fraction: fraction used for balances >= medium_threshold (default 25%)
        """
        self.min_bet = float(min_bet)
        self.max_bet = float(max_bet) if max_bet is not None else None
        self.small_threshold = float(small_threshold)
        self.medium_threshold = float(medium_threshold)
        self.small_fraction = float(small_fraction)
        self.medium_fraction = float(medium_fraction)
        self.medium_max_fraction = float(medium_max_fraction)
        self.high_fraction = float(high_fraction)

        # expose current_bet like other strategies
        self.current_bet = self.min_bet

    def _clamp_and_round(self, amount, balance):
        """Clamp amount to [min_bet, balance] and optional max_bet, round to int.

        Returns 0 if balance is 0.
        """
        if balance <= 0:
            self.current_bet = 0
            return 0

        # Do not exceed available balance
        amount = min(amount, balance)

        # Enforce max_bet if provided
        if self.max_bet is not None:
            amount = min(amount, self.max_bet)

        # Ensure at least min_bet when possible
        if amount < self.min_bet:
            # If balance < min_bet, wager whatever is left
            if balance < self.min_bet:
                amount = balance
            else:
                amount = self.min_bet

        # Use integer betting (consistent with other strategies in project)
        try:
            bet = int(round(amount))
        except Exception:
            bet = int(amount)

        self.current_bet = bet
        return bet

    def record_result(self, result, placed_bet, balance_after):
        """Return next bet based on the current balance and configured fractions.

        This strategy is balance-driven. The previous result is not used to
        change the fraction; compounding is achieved naturally because the bet
        is a fraction of the (changing) balance.
        """
        b = float(balance_after)

        if b <= 0:
            return self._clamp_and_round(0, b)

        # Small balances: all-in
        if b < self.small_threshold:
            fraction = self.small_fraction
            bet_amount = b * fraction
            return self._clamp_and_round(bet_amount, b)

        # Medium balances: interpolate between medium_max_fraction (at low end)
        # and medium_fraction (at high end) to be more aggressive when closer
        # to the small_threshold and more conservative as the balance grows.
        if self.small_threshold <= b < self.medium_threshold:
            span = self.medium_threshold - self.small_threshold
            # distance from low end (0..1)
            t = (b - self.small_threshold) / span
            # fraction goes from medium_max_fraction (t=0) -> medium_fraction (t=1)
            fraction = self.medium_max_fraction + (self.medium_fraction - self.medium_max_fraction) * t
            bet_amount = b * fraction
            return self._clamp_and_round(bet_amount, b)

        # High balances: use a smaller fraction to reduce variance
        fraction = self.high_fraction
        bet_amount = b * fraction
        return self._clamp_and_round(bet_amount, b)
