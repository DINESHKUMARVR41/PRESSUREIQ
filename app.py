import json
import random
import zipfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import parse_cricsheet_json, load_uploaded_matches
from src.analytics import build_player_summary, phase_summary, pressure_chase_summary
from src.simulator import initial_state, apply_delivery, legal_ball_outcomes
from src.recommendations import generate_recommendations
from src.win_probability import DoosraPredictor

st.set_page_config(page_title="PRESSUREIQ", page_icon="🏏", layout="wide")

st.markdown("""
<style>
.main {background: #0b1020;}
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: rgba(255,255,255,.04); padding: 14px; border-radius: 12px;}
.hero {padding: 1.5rem 1.6rem; border: 1px solid #27324a; border-radius: 18px;
background: linear-gradient(120deg, rgba(16,185,129,.16), rgba(59,130,246,.10)); margin-bottom: 1rem;}
.muted {color: #9ca3af;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🏏 PRESSUREIQ</h1>
  <h3>Cricket Pressure Management & Performance Intelligence</h3>
  <p>Turn match-state data into practical cricket training. Analyse real performance, practise difficult scenarios, and track your decisions.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Data & settings")
    st.write("Use the included sample data to explore the app, or upload Cricsheet JSON/ZIP files.")
    uploaded = st.file_uploader("Upload Cricsheet JSON or ZIP", type=["json", "zip"], accept_multiple_files=True)
    st.caption("Historical analytics only use the match files you upload. Sample rows are illustrative and clearly labelled.")

    st.divider()
    st.subheader("Doosra win-probability model")
    model_dir = st.text_input("Model folder (optional)", value="models")
    st.caption("Download the model files from the Doosra Hugging Face repository and place them in this folder. See README.md.")

matches = []
data_error = None
if uploaded:
    try:
        matches = load_uploaded_matches(uploaded)
    except Exception as exc:
        data_error = str(exc)

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Performance analytics", "Pressure simulator", "Training plan"])

if data_error:
    st.error(f"Could not read uploaded data: {data_error}")

with tab1:
    st.subheader("Your cricket performance workspace")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Matches loaded", len(matches))
    c2.metric("Analytics source", "Uploaded data" if matches else "Awaiting data")
    c3.metric("Prediction model", "Optional")
    c4.metric("Training engine", "Rule-based")
    st.info("Start by uploading Cricsheet JSON match files in the sidebar. You can also explore the simulator without historical data.")
    st.markdown("### What PRESSUREIQ does")
    a, b, c = st.columns(3)
    with a:
        st.markdown("**📊 Analyse**")
        st.write("Review batting, bowling and match-phase patterns with sample sizes.")
    with b:
        st.markdown("**🎯 Practise**")
        st.write("Play through a chase one delivery at a time and see the match state update.")
    with c:
        st.markdown("**🧭 Improve**")
        st.write("Get training suggestions based on measurable statistics—not inferred emotions.")
    if matches:
        st.success(f"Loaded {len(matches)} match file(s). Open Performance analytics to explore available player summaries.")

with tab2:
    st.subheader("Historical performance analytics")
    if not matches:
        st.warning("Upload one or more Cricsheet JSON files to enable historical analytics.")
        st.markdown("Cricsheet: https://cricsheet.org/")
    else:
        summary = build_player_summary(matches)
        if summary.empty:
            st.warning("No player rows could be calculated from the uploaded files. Confirm these are Cricsheet JSON match files.")
        else:
            players = sorted(summary["player"].dropna().unique().tolist())
            selected_player = st.selectbox("Select a player", players)
            row = summary[summary.player == selected_player].iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Runs", int(row["runs"]))
            c2.metric("Balls faced", int(row["balls_faced"]))
            c3.metric("Strike rate", f'{row["strike_rate"]:.1f}' if pd.notna(row["strike_rate"]) else "—")
            c4.metric("Dismissals recorded", int(row["dismissals"]))
            st.caption(f"Batting summary across {int(row['innings'])} innings in the uploaded sample. Data coverage depends on the files supplied.")
            phases = phase_summary(matches, selected_player)
            if not phases.empty:
                st.markdown("#### Performance by innings phase")
                fig = px.bar(phases, x="phase", y="runs", color="phase", title="Runs scored by phase")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(phases, use_container_width=True, hide_index=True)
            pressure = pressure_chase_summary(matches, selected_player)
            if not pressure.empty:
                st.markdown("#### Chase situations")
                st.dataframe(pressure, use_container_width=True, hide_index=True)
            st.markdown("#### Player summaries")
            st.dataframe(summary.sort_values("runs", ascending=False), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Interactive T20 chase simulator")
    st.write("This simulator uses transparent rules. Delivery outcomes are chosen by you; it does not claim to measure emotions.")
    left, right = st.columns([1, 1])
    with left:
        target = st.number_input("Target score", min_value=1, max_value=400, value=177, step=1)
        starting_score = st.number_input("Current score", min_value=0, max_value=399, value=151, step=1)
        wickets_fallen = st.number_input("Wickets fallen", min_value=0, max_value=9, value=4, step=1)
        balls_left = st.number_input("Balls remaining", min_value=1, max_value=120, value=24, step=1)
        venue_par = st.number_input("Venue par (optional model input)", min_value=0, max_value=400, value=159, step=1)
        elo_diff = st.number_input("Batting team Elo minus bowling team Elo", min_value=-1000, max_value=1000, value=0, step=10)
        if st.button("Start / reset scenario", type="primary"):
            st.session_state.sim_state = initial_state(int(target), int(starting_score), int(wickets_fallen), int(balls_left))
            st.session_state.sim_log = []
    with right:
        if "sim_state" not in st.session_state:
            st.session_state.sim_state = initial_state(int(target), int(starting_score), int(wickets_fallen), int(balls_left))
            st.session_state.sim_log = []
        state = st.session_state.sim_state
        need = max(0, state["target"] - state["score"])
        req_rate = (need * 6 / state["balls_left"]) if state["balls_left"] else 0
        m1, m2, m3 = st.columns(3)
        m1.metric("Score", f'{state["score"]}/{state["wickets"]}')
        m2.metric("Runs needed", need)
        m3.metric("Balls left", state["balls_left"])
        st.metric("Required run rate", f"{req_rate:.2f}" if state["balls_left"] else "0.00")
        predictor = DoosraPredictor(model_dir)
        probability = predictor.predict(
            innings=2, score=state["score"], wickets=state["wickets"],
            balls_left=state["balls_left"], target=state["target"],
            venue_par=int(venue_par) if venue_par else None, elo_diff=int(elo_diff)
        )
        if probability is not None:
            st.metric("Estimated batting-team win probability", f"{probability:.1%}")
            st.caption("Prediction from the optional Doosra model. It is an estimate, not a pressure or mental-strength score.")
        else:
            st.info("Doosra model not loaded. The simulator works without it. See README.md to enable predictions.")
        if state["status"] != "In progress":
            st.success(state["status"])
    disabled = st.session_state.sim_state["status"] != "In progress"
    st.markdown("#### Choose the next delivery outcome")
    outcomes = legal_ball_outcomes()
    labels = {0: "Dot ball", 1: "1 run", 2: "2 runs", 3: "3 runs", 4: "Four", 6: "Six", "W": "Wicket", "WD": "Wide (+1 run, no ball used)", "NB": "No-ball (+1 run, no ball used)"}
    selected = st.selectbox("Outcome", list(outcomes), format_func=lambda x: labels[x], disabled=disabled)
    if st.button("Apply delivery", disabled=disabled):
        state, event = apply_delivery(st.session_state.sim_state, selected)
        st.session_state.sim_state = state
        st.session_state.sim_log.append(event)
        st.rerun()
    if st.session_state.sim_log:
        log_df = pd.DataFrame(st.session_state.sim_log)
        st.markdown("#### Delivery log")
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        st.download_button("Download scenario log (CSV)", log_df.to_csv(index=False), "pressureiq_scenario.csv", "text/csv")

with tab4:
    st.subheader("Training recommendations")
    if matches:
        summary = build_player_summary(matches)
        if not summary.empty:
            chosen = st.selectbox("Player for recommendations", sorted(summary.player.unique()), key="recommend_player")
            player_row = summary[summary.player == chosen].iloc[0].to_dict()
            phase = phase_summary(matches, chosen)
            recs = generate_recommendations(player_row, phase)
            st.caption("Recommendations are simple rules based on observed statistics. They are not medical or psychological advice.")
            for rec in recs:
                with st.container(border=True):
                    st.markdown(f"**{rec['title']}**")
                    st.write(rec["reason"])
                    st.write(f"**Suggested practice:** {rec['drill']}")
    else:
        st.info("Upload match data to get data-supported recommendations. General reset routines are available below.")
    with st.expander("Between-delivery reset routine"):
        st.markdown("""
        1. Step away from the previous delivery for a moment.
        2. Take one comfortable, controlled breath.
        3. Choose one specific cue for the next ball (for example, line and length).
        4. Commit to the plan and return attention to the current delivery.
        """)
    with st.expander("Pre-over checklist"):
        st.markdown("""
        - What is the match situation?
        - What is the batter likely trying to do?
        - What is my primary plan?
        - What is my backup plan?
        - What will I focus on after the delivery?
        """)

st.divider()
st.caption("PRESSUREIQ • Cricket analytics and training support • Predictions are estimates; historical and simulated data are shown separately.")
