from pathlib import Path
import sys


class DoosraPredictor:
    """Optional adapter for the Doosra repository. App remains usable without the model."""

    def __init__(self, model_dir="models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.error = None
        try:
            repo_dir = self.model_dir.resolve()
            if repo_dir.exists() and str(repo_dir) not in sys.path:
                sys.path.insert(0, str(repo_dir))
            from predict import WinProbability
            model_path = repo_dir / "winprob-t20.json"
            if model_path.exists():
                self.model = WinProbability(str(model_path))
        except Exception as exc:
            self.error = str(exc)

    def predict(self, innings, score, wickets, balls_left, target=None, venue_par=None, elo_diff=0):
        if self.model is None:
            return None
        try:
            kwargs = {
                "innings": int(innings),
                "score": int(score),
                "wickets": int(wickets),
                "balls_left": int(balls_left),
            }
            if target is not None:
                kwargs["target"] = int(target)
            if venue_par is not None:
                kwargs["venue_par"] = int(venue_par)
            if elo_diff is not None:
                kwargs["elo_diff"] = int(elo_diff)
            value = float(self.model.predict(**kwargs))
            return max(0.0, min(1.0, value))
        except Exception as exc:
            self.error = str(exc)
            return None
