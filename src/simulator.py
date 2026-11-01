def initial_state(target, score=0, wickets=0, balls_left=120):
    state = {
        "target": int(target), "score": int(score), "wickets": int(wickets),
        "balls_left": int(balls_left), "status": "In progress"
    }
    return _update_status(state)


def legal_ball_outcomes():
    return [0, 1, 2, 3, 4, 6, "W", "WD", "NB"]


def apply_delivery(state, outcome):
    new = dict(state)
    runs = 0
    wicket = 0
    legal = True
    if outcome == "W":
        wicket = 1
    elif outcome == "WD":
        runs = 1
        legal = False
    elif outcome == "NB":
        runs = 1
        legal = False
    else:
        runs = int(outcome)
    new["score"] += runs
    new["wickets"] += wicket
    if legal:
        new["balls_left"] = max(0, new["balls_left"] - 1)
    new = _update_status(new)
    event = {
        "outcome": str(outcome),
        "runs_added": runs,
        "wicket": wicket,
        "legal_ball": legal,
        "score": f'{new["score"]}/{new["wickets"]}',
        "runs_needed": max(0, new["target"] - new["score"]),
        "balls_left": new["balls_left"],
        "status": new["status"],
    }
    return new, event


def _update_status(state):
    if state["score"] >= state["target"]:
        state["status"] = "Target achieved"
    elif state["wickets"] >= 10:
        state["status"] = "All out"
    elif state["balls_left"] <= 0:
        state["status"] = "Chase complete — target not reached"
    else:
        state["status"] = "In progress"
    return state
