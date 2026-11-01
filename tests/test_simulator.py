from src.simulator import initial_state, apply_delivery


def test_legal_delivery_reduces_balls():
    state = initial_state(target=10, score=0, wickets=0, balls_left=6)
    state, _ = apply_delivery(state, 1)
    assert state["score"] == 1
    assert state["balls_left"] == 5


def test_wide_does_not_reduce_balls():
    state = initial_state(target=10, score=0, wickets=0, balls_left=6)
    state, _ = apply_delivery(state, "WD")
    assert state["score"] == 1
    assert state["balls_left"] == 6


def test_target_achieved():
    state = initial_state(target=2, score=1, wickets=0, balls_left=3)
    state, _ = apply_delivery(state, 1)
    assert state["status"] == "Target achieved"
