# Tournament Analysis

Small Streamlit app for checking the Chinese Checkers tournament results

I used it to look at our team and export plots for the report

Demo video: [`media/streamlit-demo.mov`](media/streamlit-demo.mov)

## Run it

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit page in the browser

## Files

```text
app.py          starts the dashboard
analysis.py     reads the tournament files
charts.py       makes the plots
requirements.txt packages needed to run the app
data/           round files from the tournament
```

## What it shows

- leaderboard
- team summary
- score over rounds
- score parts
- head to head results
- skipped turns
- player count and colour results

## Export plots

Choose a team in the sidebar

Click `Build PNG zip`

Then download the zip file with the plots and leaderboard CSV

## Note

This app is only for analysing tournament results

It does not use the game agent or model files
