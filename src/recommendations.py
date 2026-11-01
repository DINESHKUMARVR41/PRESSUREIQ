def generate_recommendations(player_row, phase_df):
    recommendations = []
    runs = int(player_row.get("runs", 0) or 0)
    balls = int(player_row.get("balls_faced", 0) or 0)
    sr = player_row.get("strike_rate")
    innings = int(player_row.get("innings", 0) or 0)

    if balls < 30:
        recommendations.append({
            "title": "Build a larger performance sample",
            "reason": f"The selected player has {balls} legal balls in the uploaded sample. That is too little to draw strong conclusions about a consistent pattern.",
            "drill": "Record several structured net sessions and compare outcomes across sessions before drawing conclusions."
        })
    elif sr is not None and sr < 100:
        recommendations.append({
            "title": "Practise controlled scoring options",
            "reason": f"The observed strike rate is {sr:.1f} across {balls} legal balls. Context, format, role and match situation matter, so this is a prompt for review rather than a judgement.",
            "drill": "Run a 12-ball scenario and practise rotating strike while selecting a few boundary-scoring options."
        })
    elif sr is not None:
        recommendations.append({
            "title": "Maintain scoring options under constraints",
            "reason": f"The observed strike rate is {sr:.1f} across {balls} legal balls. This summary alone does not establish performance quality without role and match context.",
            "drill": "Practise a 12-ball scenario with a target score and track both runs and dismissals."
        })

    if phase_df is not None and not phase_df.empty and "phase" in phase_df.columns:
        death = phase_df[phase_df["phase"] == "Death (15+)"]
        middle = phase_df[phase_df["phase"] == "Middle (6-14)"]
        if not death.empty and int(death.iloc[0]["legal_balls"]) >= 12:
            death_sr = death.iloc[0]["strike_rate"]
            middle_sr = middle.iloc[0]["strike_rate"] if not middle.empty else None
            if death_sr is not None and middle_sr is not None and death_sr < middle_sr:
                recommendations.append({
                    "title": "Review death-over scoring options",
                    "reason": f"Death-over strike rate ({death_sr:.1f}) is below the middle-over rate ({middle_sr:.1f}) in this uploaded sample. This may reflect role, bowling quality, wickets, or sample composition.",
                    "drill": "Practise the final 12 balls of an innings with a defined target and review shot selection after each attempt."
                })
    if not recommendations:
        recommendations.append({
            "title": "Keep tracking practice",
            "reason": f"The current sample covers {innings} innings. More context may be needed before a specific pattern is identified.",
            "drill": "Repeat a consistent scenario and record outcomes over multiple sessions."
        })
    return recommendations
