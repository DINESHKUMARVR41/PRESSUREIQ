from pathlib import Path
import sys

MODEL_DIR = Path(__file__).parent / "models"
sys.path.insert(0, str(MODEL_DIR))

from predict import WinProbability

wp = WinProbability(str(MODEL_DIR / "winprob-t20.json"))

probability = wp.predict(
    innings=2,
    score=151,
    wickets=4,
    balls_left=24,
    target=177,
    venue_par=159,
    elo_diff=-123
)

print(f"Predicted win probability: {probability:.1%}")