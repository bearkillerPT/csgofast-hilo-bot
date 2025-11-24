import os
from os import path


def _load_dotenv(env_path: str):
    """Simple .env loader: read key=value pairs and set them in os.environ
    if they are not already set. This keeps the project dependency-free.
    """
    if not path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # don't overwrite existing environment variables
            if key not in os.environ:
                os.environ[key] = val


class EnvConfig:
    """Load environment variables (optionally from .env) and provide factory
    methods to create configured strategy objects.

    Usage:
        cfg = EnvConfig(project_root)
        strategy = cfg.get_strategy(base_bet)
    """

    def __init__(self, project_root: str = None):
        self.project_root = project_root or path.dirname(path.abspath(__file__))
        self.env_path = path.join(self.project_root, ".env")
        _load_dotenv(self.env_path)
        self.strategy_name = os.environ.get("BET_STRATEGY", "paroli").lower()
        # base bet (can be integer or float in .env)
        self.base_bet = self._get_float("BASE_BET", 25)

    def _get_int(self, name: str, default: int):
        raw = os.environ.get(name)
        if raw is None or raw == "":
            return default
        try:
            return int(raw)
        except ValueError:
            return int(float(raw))

    def _get_float(self, name: str, default: float):
        raw = os.environ.get(name)
        if raw is None or raw == "":
            return default
        try:
            return float(raw)
        except ValueError:
            return default

    def get_strategy(self, base_bet: float):
        """Return an instantiated strategy object configured from env vars.

        base_bet is used as a fallback for strategy min/base bet values.
        """
        name = self.strategy_name

        if name == "martingale":
            multiplier = self._get_float("MARTINGALE_MULTIPLIER", 2)
            from strategies.martingale import MartingaleStrategy

            return MartingaleStrategy(base_bet=base_bet, multiplier=multiplier)

        if name == "paroli":
            multiplier = self._get_float("PAROLI_MULTIPLIER", 2)
            target = self._get_int("PAROLI_TARGET_STREAK", 3)
            from strategies.paroli import ParoliStrategy

            return ParoliStrategy(base_bet=base_bet, multiplier=multiplier, target_streak=target)

        if name == "fractional":
            min_bet = self._get_float("FRACTIONAL_MIN_BET", base_bet)
            max_bet_raw = os.environ.get("FRACTIONAL_MAX_BET")
            max_bet = float(max_bet_raw) if max_bet_raw not in (None, "") else None

            small_threshold = self._get_float("FRACTIONAL_SMALL_THRESHOLD", 500)
            medium_threshold = self._get_float("FRACTIONAL_MEDIUM_THRESHOLD", 5000)
            small_fraction = self._get_float("FRACTIONAL_SMALL_FRACTION", 1.0)
            medium_fraction = self._get_float("FRACTIONAL_MEDIUM_FRACTION", 0.5)
            medium_max_fraction = self._get_float("FRACTIONAL_MEDIUM_MAX_FRACTION", 0.75)
            high_fraction = self._get_float("FRACTIONAL_HIGH_FRACTION", 0.25)

            from strategies.fractional import FractionalStrategy

            return FractionalStrategy(
                min_bet=min_bet,
                max_bet=max_bet,
                small_threshold=small_threshold,
                medium_threshold=medium_threshold,
                small_fraction=small_fraction,
                medium_fraction=medium_fraction,
                medium_max_fraction=medium_max_fraction,
                high_fraction=high_fraction,
            )

        # fallback: Paroli (matches previous default behaviour)
        multiplier = self._get_float("PAROLI_MULTIPLIER", 2)
        target = self._get_int("PAROLI_TARGET_STREAK", 3)
        from strategies.paroli import ParoliStrategy

        return ParoliStrategy(base_bet=base_bet, multiplier=multiplier, target_streak=target)
