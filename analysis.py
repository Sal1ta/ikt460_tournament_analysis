# Reads tournament round files
# Builds leaderboard and team summaries

import csv
import statistics
import urllib.request
from collections import defaultdict
from pathlib import Path

REPO_BASE = "https://raw.githubusercontent.com/cair/RLChineseCheckers/main/tournament%20results"
HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "data"
DEFAULT_TEAM = "S&S"
NUM_ROUNDS = 13


# Parse round files

def _parse_kv_cell(cell):
    # Split packed cells into a dictionary
    out = {}
    if not cell or cell == "NA":
        return out
    for chunk in cell.split(";"):
        if ":" not in chunk:
            continue
        name, val = chunk.rsplit(":", 1)
        out[name.strip()] = val.strip()
    return out


def _to_float(d):
    return {k: float(v) for k, v in d.items() if v not in ("", "NA")}


def _to_int(d):
    return {k: int(float(v)) for k, v in d.items() if v not in ("", "NA")}


def parse_round(path, round_no):
    games = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scores  = _to_float(_parse_kv_cell(row["final_scores"]))
            pins    = _to_float(_parse_kv_cell(row["pin_scores"]))
            times   = _to_float(_parse_kv_cell(row["time_scores"]))
            dists   = _to_float(_parse_kv_cell(row["distance_scores"]))
            moves   = _to_float(_parse_kv_cell(row["move_scores"]))
            skipped = _to_int(_parse_kv_cell(row["skipped_turns"]))
            winner  = (row.get("winner") or "").strip()
            # Read colour per team from the joined cell
            colors  = _parse_kv_cell(row.get("joined", ""))
            n = len(scores)
            ranked = sorted(scores.items(), key=lambda kv: -kv[1])
            rank_of = {name: i + 1 for i, (name, _) in enumerate(ranked)}
            games.append({
                "round": round_no,
                "game_id": row["game_number"],
                "n_players": n,
                "winner": winner if winner and winner != "None" else None,
                "scores": scores,
                "pins": pins,
                "times": times,
                "dists": dists,
                "moves": moves,
                "skipped": skipped,
                "rank": rank_of,
                "colors": colors,
            })
    return games


# Build team summaries

def aggregate(all_games):
    stats = defaultdict(lambda: {
        "games": 0,
        "wins": 0,
        "scores": [],
        "ranks": [],
        "pins": [],
        "times": [],
        "moves": [],
        "dists": [],
        "skipped": [],
    })
    for g in all_games:
        n = g["n_players"]
        if n == 0:
            continue
        for name, sc in g["scores"].items():
            s = stats[name]
            s["games"]     += 1
            s["wins"]      += int(g["winner"] == name)
            s["scores"].append(sc)
            r = g["rank"][name]
            s["ranks"].append(r)
            if name in g["pins"]:    s["pins"].append(g["pins"][name] / 100.0)
            if name in g["times"]:   s["times"].append(g["times"][name])
            if name in g["moves"]:   s["moves"].append(g["moves"][name])
            if name in g["dists"]:   s["dists"].append(g["dists"][name])
            if name in g["skipped"]: s["skipped"].append(g["skipped"][name])
    # Use normal dicts for Streamlit cache
    return {name: dict(values) for name, values in stats.items()}


def _mean(xs):
    return statistics.mean(xs) if xs else float("nan")


def leaderboard(stats):
    rows = []
    for name, s in stats.items():
        if s["games"] == 0:
            continue
        rows.append({
            "team":       name,
            "games":      s["games"],
            "wins":       s["wins"],
            "win_rate":   s["wins"] / s["games"],
            "mean_score": _mean(s["scores"]),
            "mean_rank":  _mean(s["ranks"]),
            "mean_pins":  _mean(s["pins"]),
            "mean_time":  _mean(s["times"]),
            "mean_moves": _mean(s["moves"]),
            "mean_dist":  _mean(s["dists"]),
            "total_skip": sum(s["skipped"]),
        })
    rows.sort(key=lambda r: -r["mean_score"])
    return rows


# Download missing round files

def ensure_downloaded(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    for i in range(1, NUM_ROUNDS + 1):
        path = data_dir / f"round{i}.txt"
        if path.exists():
            continue
        url = f"{REPO_BASE}/round{i}.txt"
        try:
            urllib.request.urlretrieve(url, path)
        except Exception as exc:
            # Round may not exist yet or network unavailable — skip silently
            if path.exists():
                path.unlink()   # remove partial download
            print(f"Could not download round {i}: {exc}")
