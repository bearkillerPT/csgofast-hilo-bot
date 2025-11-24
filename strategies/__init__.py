"""Strategies package for betting algorithms.

This package exposes strategy classes with a common API:
  - record_result(result, placed_bet, balance_after) -> next_bet

Add more strategies here as needed.
"""

__all__ = ["MartingaleStrategy", "ParoliStrategy"]
