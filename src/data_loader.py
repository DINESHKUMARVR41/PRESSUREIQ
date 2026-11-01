import json
import zipfile
from io import BytesIO
from pathlib import Path


def parse_cricsheet_json(data):
    """Parse one Cricsheet JSON match into a normalized list of deliveries."""
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    match = json.loads(data) if isinstance(data, str) else data
    info = match.get("info", {})
    teams = info.get("teams", [])
    innings_rows = []
    for innings_number, innings in enumerate(match.get("innings", []), start=1):
        batting_team = innings.get("team", "Unknown")
        over_list = innings.get("overs", [])
        for over in over_list:
            over_number = int(over.get("over", 0))
            for delivery_index, delivery in enumerate(over.get("deliveries", [])):
                batter = delivery.get("batter") or delivery.get("striker") or "Unknown"
                bowler = delivery.get("bowler", "Unknown")
                runs = delivery.get("runs", {})
                extras = delivery.get("extras", {}) or {}
                total_runs = int(runs.get("total", 0))
                batter_runs = int(runs.get("batter", 0))
                nonlegal = any(key in extras for key in ("wides", "noballs"))
                wickets = delivery.get("wickets", []) or []
                dismissed = [w.get("player_out") for w in wickets if w.get("player_out")]
                innings_rows.append({
                    "match_id": info.get("match_type", "unknown") + "_" + str(info.get("dates", ["unknown"])[0]),
                    "date": str(info.get("dates", [""])[0]),
                    "match_type": info.get("match_type", "unknown"),
                    "gender": info.get("gender", "unknown"),
                    "teams": " vs ".join(teams),
                    "innings": innings_number,
                    "batting_team": batting_team,
                    "over": over_number,
                    "delivery_index": delivery_index,
                    "batter": batter,
                    "bowler": bowler,
                    "batter_runs": batter_runs,
                    "total_runs": total_runs,
                    "extras": sum(int(v) for v in extras.values() if isinstance(v, (int, float))),
                    "is_legal_ball": not nonlegal,
                    "wickets": len(wickets),
                    "dismissed_players": dismissed,
                })
    return innings_rows


def load_uploaded_matches(uploaded_files):
    rows = []
    for uploaded in uploaded_files:
        name = uploaded.name.lower()
        content = uploaded.getvalue()
        if name.endswith(".json"):
            rows.extend(parse_cricsheet_json(content))
        elif name.endswith(".zip"):
            with zipfile.ZipFile(BytesIO(content)) as archive:
                for member in archive.namelist():
                    if member.lower().endswith(".json") and not member.startswith("__MACOSX"):
                        try:
                            rows.extend(parse_cricsheet_json(archive.read(member)))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
    return rows
