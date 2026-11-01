# PRESSUREIQ 🏏
**Cricket Pressure Management & Performance Intelligence**

PRESSUREIQ is a cricket analytics and training MVP that combines historical match statistics, a delivery-by-delivery T20 chase simulator, optional win-probability prediction, and rule-based training recommendations.

## MVP features

- Upload Cricsheet JSON files or ZIP archives containing Cricsheet JSON.
- Calculate batter runs, legal balls, strike rate, innings count and recorded dismissals.
- View batting performance by powerplay, middle overs and death overs.
- Explore second-innings and death-over summaries.
- Simulate a T20 chase one delivery at a time.
- Optionally connect the pretrained Doosra T20 win-probability model.
- View rule-based training recommendations and general between-delivery reset routines.
- Export a simulator delivery log to CSV.

## Requirements

- Windows 10/11
- Python 3.11 recommended
- Internet connection only to download dependencies and datasets/models

## Run on Windows PowerShell

1. Download and extract this project.
2. Open the `PRESSUREIQ` folder in VS Code.
3. Open the VS Code terminal (PowerShell) and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Add historical data

1. Visit https://cricsheet.org/
2. Download the desired match data in JSON format.
3. In PRESSUREIQ, use the sidebar uploader to upload one or more JSON files or a ZIP archive containing JSON files.

Start with a small set of T20 matches to validate the parsing and metrics before uploading a larger dataset.

### Data and analytics notes

- The application only analyses match files that you upload.
- Phase boundaries in this MVP are over-number based: powerplay 0–5, middle 6–14, death 15+. Confirm format and innings length before interpreting.
- The player summary aggregates all uploaded files. The current match identifier is a lightweight identifier and is not guaranteed to be globally unique.
- The chase summary is an approximate batter-level summary, not a full reconstructed ball-by-ball match-state analysis.
- Bowling economy, full innings reconstruction, player-vs-player comparisons, and robust match-level pressure labels are future improvements.
- Statistics are descriptive and do not establish a player's emotional state or psychological condition.

## Optional: Doosra win-probability model

Repository/model card:
https://huggingface.co/Sarthak213/doosra-win-probability

The model card describes T20 and ODI models and documents a NumPy-oriented `predict.py` interface. This application currently integrates the T20 prediction path as an optional feature.

To enable it:

1. Download the repository files from Hugging Face, including `predict.py` and `winprob-t20.json`.
2. Create a `models` folder in the project root.
3. Place those files inside `models`, so the structure is:

```text
PRESSUREIQ/
├── app.py
├── models/
│   ├── predict.py
│   └── winprob-t20.json
└── ...
```

4. Restart the app. The model path can be changed in the sidebar.

If the model is unavailable, the analytics and simulator continue to work. Do not fabricate missing model inputs. `venue_par` and `elo_diff` should be supplied from valid historical information when available; otherwise document that default values are being used.

### License and attribution

- Cricsheet data: review the current terms on https://cricsheet.org/ before redistribution. The Doosra model card states that its data and model are released under ODC-By 1.0 and requests credit to Cricsheet and Doosra. Verify the terms for the exact files you use.
- Doosra model: https://huggingface.co/Sarthak213/doosra-win-probability
- Do not redistribute downloaded datasets or model artifacts without checking their applicable terms.
- This repository's code is provided as an MVP scaffold; add an explicit project license before public reuse if needed.

## Test

```powershell
python -m pytest -q
```

## Project structure

```text
PRESSUREIQ/
├── app.py
├── requirements.txt
├── README.md
├── data/
├── src/
│   ├── data_loader.py
│   ├── analytics.py
│   ├── simulator.py
│   ├── recommendations.py
│   └── win_probability.py
├── tests/
└── outputs/
```

## Known limitations

- The simulator is a simplified chase-state tool. It does not model every cricket rule or all extra-ball edge cases.
- The Doosra prediction adapter is optional and has not been verified against downloaded model files in every environment.
- Uploaded data coverage determines the reliability of all descriptive statistics.
- Recommendations are simple rules, not scientifically validated psychological or performance diagnoses.
- This MVP does not train any machine-learning model.
