import pandas as pd


def _frame(matches):
    df = pd.DataFrame(matches)
    if df.empty:
        return df
    df["over"] = pd.to_numeric(df["over"], errors="coerce").fillna(0).astype(int)
    return df


def build_player_summary(matches):
    df = _frame(matches)
    if df.empty:
        return pd.DataFrame()
    rows = []
    for player, group in df.groupby("batter"):
        balls = int(group["is_legal_ball"].sum())
        runs = int(group["batter_runs"].sum())
        dismissals = sum(player in (dismissed or []) for dismissed in group["dismissed_players"])
        innings = int(group["innings"].nunique())
        rows.append({
            "player": player,
            "runs": runs,
            "balls_faced": balls,
            "strike_rate": (runs / balls * 100) if balls else None,
            "dismissals": int(dismissals),
            "innings": innings,
            "matches_in_sample": int(group["match_id"].nunique()),
        })
    return pd.DataFrame(rows).sort_values("runs", ascending=False)


def phase_summary(matches, player):
    df = _frame(matches)
    if df.empty:
        return pd.DataFrame()
    df = df[df["batter"] == player].copy()
    if df.empty:
        return pd.DataFrame()
    def phase(over):
        if over < 6:
            return "Powerplay (0-5)"
        if over < 15:
            return "Middle (6-14)"
        return "Death (15+)"
    df["phase"] = df["over"].map(phase)
    result = df.groupby("phase", as_index=False).agg(
        runs=("batter_runs", "sum"),
        legal_balls=("is_legal_ball", "sum"),
        deliveries=("batter_runs", "count"),
        dismissals=("wickets", "sum"),
    )
    result["strike_rate"] = result.apply(lambda r: (r["runs"] / r["legal_balls"] * 100) if r["legal_balls"] else None, axis=1)
    return result


def pressure_chase_summary(matches, player):
    df = _frame(matches)
    if df.empty:
        return pd.DataFrame()
    # Approximate batter-level context from the uploaded innings; full match-state reconstruction is outside this MVP.
    df = df[(df["batter"] == player) & (df["innings"] == 2)].copy()
    if df.empty:
        return pd.DataFrame()
    df["high_over"] = df["over"] >= 15
    rows = []
    for label, group in [("All second-innings deliveries", df), ("Death overs in second innings", df[df["high_over"]])]:
        balls = int(group["is_legal_ball"].sum())
        runs = int(group["batter_runs"].sum())
        rows.append({"situation": label, "runs": runs, "legal_balls": balls, "strike_rate": (runs / balls * 100) if balls else None, "deliveries_in_sample": len(group)})
    return pd.DataFrame(rows)
