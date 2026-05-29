# Plotly chart functions for the tournament analysis app

from collections import defaultdict
import statistics
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


THEMES = {
    "light": {
        # Light theme colors
        "BG":          "#FFFFFF",   # pure white canvas
        "GRID":        "#E2E8F0",   # slate-200 grid
        "TEXT":        "#0F172A",   # slate-900 primary text
        "SUBTLE":      "#475569",   # slate-600 secondary text
        "MUTED":       "#94A3B8",   # slate-400 footnote text
        "OTHER":       "#CBD5E1",   # slate-300 recedes vs accent on white
        # Selected team colors
        "HIGHLIGHT":   "#0D9488",   # teal-600
        "HIGHLIGHT_W": "#0F766E",   # teal-700 outlines/markers/win-stars
        # Extra chart colors
        "BLUE":        "#0EA5E9",   # sky-500 soft blue
        "GREEN":       "#10B981",   # emerald-500 soft green
        "TEAL":        "#14B8A6",   # teal-500 secondary accent
        "INDIGO":      "#6366F1",   # indigo-500 distinguishable but soft
        "ORANGE":      "#F59E0B",   # amber-500 softened warning
        # Heatmap colors
        "HEAT_LOW":    "#60A5FA",   # blue-400 row loses
        "HEAT_MID":    "#F1F5F9",   # slate-100 neutral midpoint
        "HEAT_HIGH":   "#34D399",   # emerald-400 row dominates
        "HOVER_BG":    "#F8FAFC",   # slate-50 hover-card background
    },
    "dark": {
        "BG": "#0B1220",
        "GRID": "#243044",
        "TEXT": "#E5E7EB",
        "SUBTLE": "#CBD5E1",
        "MUTED": "#94A3B8",
        "OTHER": "#475569",
        "HIGHLIGHT": "#60A5FA",
        "HIGHLIGHT_W": "#93C5FD",
        "BLUE": "#60A5FA",
        "GREEN": "#34D399",
        "TEAL": "#2DD4BF",
        "INDIGO": "#818CF8",
        "ORANGE": "#FBBF24",
        "HEAT_LOW": "#2563EB",
        "HEAT_MID": "#111827",
        "HEAT_HIGH": "#22C55E",
        "HOVER_BG": "#111827",
    },
}

# globals() makes all colour constants immediately available without passing
# a theme argument into every chart function
BG = GRID = TEXT = SUBTLE = MUTED = OTHER = HIGHLIGHT = HIGHLIGHT_W = ""
BLUE = GREEN = TEAL = INDIGO = ORANGE = HEAT_LOW = HEAT_MID = HEAT_HIGH = HOVER_BG = ""


def set_theme(theme="light"):
    values = THEMES.get(theme, THEMES["light"])
    globals().update(values)


set_theme("light")


def _base_layout(title=None, height=520, ymargin=80):
    # Every chart inherits these defaults so Plotly layout options stay in one place
    layout = dict(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family="Inter, Helvetica, Arial, sans-serif",
                  size=12, color=TEXT),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID,
                   linecolor=GRID, tickfont=dict(color=SUBTLE)),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID,
                   linecolor=GRID, tickfont=dict(color=SUBTLE)),
        height=height,
        margin=dict(l=ymargin, r=20, t=50 if title else 20, b=50),
        hoverlabel=dict(bgcolor=HOVER_BG,
                        bordercolor=GRID,
                        font=dict(family="Inter", size=12, color=TEXT)),
        legend=dict(bgcolor="rgba(0,0,0,0)",
                    bordercolor=GRID, borderwidth=0,
                    font=dict(color=TEXT)),
    )
    if title:
        layout["title"] = dict(text=title, font=dict(size=14, color=TEXT,
                                                     family="Inter"))
    return layout


def timeline_chart(all_games, team):
    # Show the selected teams score in every game with stars marking wins
    games = [g for g in all_games if team in g["scores"]]
    if not games:
        return _empty(f"No games for {team!r}")
    xs   = [f"R{g['round']}" for g in games]
    ys   = [g["scores"][team] for g in games]
    wins = [g["winner"] == team for g in games]
    win_x = [x for x, w in zip(xs, wins) if w]
    win_y = [y for y, w in zip(ys, wins) if w]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines+markers",
        line=dict(color=HIGHLIGHT_W, width=3, shape="spline"),
        marker=dict(size=10, color=HIGHLIGHT,
                    line=dict(color=HIGHLIGHT_W, width=2)),
        hovertemplate="<b>%{x}</b><br>Score: %{y:.0f}<extra></extra>",
        name="score",
    ))
    if win_x:
        fig.add_trace(go.Scatter(
            x=win_x, y=win_y, mode="markers",
            marker=dict(size=20, symbol="star",
                        color=GREEN,
                        line=dict(color=BG, width=1)),
            hovertemplate="<b>%{x} — WIN</b><br>Score: %{y:.0f}<extra></extra>",
            name="win",
        ))
    mean_y = float(np.mean(ys))
    fig.add_hline(y=mean_y, line_dash="dash", line_color=SUBTLE,
                  line_width=1,
                  annotation_text=f"mean {mean_y:.0f}",
                  annotation_position="top right",
                  annotation_font_color=SUBTLE,
                  annotation_font_size=10)

    layout = _base_layout(height=460)
    layout["yaxis"]["title"] = dict(text="Final score",
                                    font=dict(color=SUBTLE, size=11))
    fig.update_layout(**layout, showlegend=False)
    return fig


def head_to_head_chart(all_games, team):
    # Count how often the selected team placed above or below each opponent
    # across all games they shared, then sort opponents by net advantage
    wins, losses = defaultdict(int), defaultdict(int)
    for g in all_games:
        if team not in g["scores"]:
            continue
        my_rank = g["rank"][team]
        for opp, _ in g["scores"].items():
            if opp == team:
                continue
            if g["rank"][opp] > my_rank:
                wins[opp] += 1
            elif g["rank"][opp] < my_rank:
                losses[opp] += 1
    if not wins and not losses:
        return _empty(f"No head-to-head data for {team!r}")

    opponents = sorted(set(wins) | set(losses),
                       key=lambda o: (wins[o] - losses[o], wins[o] + losses[o]))
    w = [wins[o]   for o in opponents]
    l = [losses[o] for o in opponents]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=w, y=opponents, orientation="h", name=f"{team} higher",
        marker=dict(color=GREEN, line=dict(width=0)),
        text=[f"{x}" if x > 0 else "" for x in w], textposition="inside",
        textfont=dict(color="#052E1E", size=11),
        hovertemplate=f"<b>{team} finished higher</b><br>"
                      "%{y}: %{x} game(s)<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=l, y=opponents, orientation="h", name="opponent higher",
        marker=dict(color=BLUE, line=dict(width=0)),
        text=[f"{x}" if x > 0 else "" for x in l], textposition="inside",
        textfont=dict(color="#082F49", size=11),
        hovertemplate="<b>opponent finished higher</b><br>"
                      "%{y}: %{x} game(s)<extra></extra>",
    ))
    layout = _base_layout(height=max(420, 24 * len(opponents)), ymargin=180)
    layout["xaxis"]["title"] = dict(text="Number of meetings",
                                    font=dict(color=SUBTLE, size=11))
    fig.update_layout(**layout, barmode="stack")
    return fig


def components_chart(stats, team, top_n=5):
    # Show the top teams and the selected team side by side with each score
    # component stacked so it is easy to see where the gap comes from
    ranked = sorted(stats.items(),
                    key=lambda kv: -np.mean(kv[1]["scores"] or [0]))
    picked = [name for name, _ in ranked[:top_n]]
    if team not in picked and stats.get(team):
        picked.append(team)

    def _m(name, key, scale=1.0):
        xs = stats[name][key]
        return float(np.mean(xs)) * scale if xs else 0.0

    pin   = [_m(n, "pins", scale=100.0) for n in picked]
    tim   = [_m(n, "times") for n in picked]
    mov   = [_m(n, "moves") for n in picked]
    total = [_m(n, "scores") for n in picked]
    dist  = [max(0, t - p - tm - mv) for t, p, tm, mv in
             zip(total, pin, tim, mov)]

    # Highlight selected team labels
    tick_labels = [
        f'<span style="color:{HIGHLIGHT_W};font-weight:600">{n}</span>'
        if n == team
        else f'<span style="color:{SUBTLE}">{n}</span>'
        for n in picked
    ]

    fig = go.Figure()
    for label, vals, color in [
        ("Pins (×100)",     pin,  GREEN),
        ("Distance (≤400)", dist, BLUE),
        ("Move (≤100)",     mov,  TEAL),
        ("Time (≤100)",     tim,  INDIGO),
    ]:
        fig.add_trace(go.Bar(
            x=tick_labels, y=vals, name=label,
            marker=dict(color=color, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>" + label + ": %{y:.0f}<extra></extra>",
        ))
    layout = _base_layout(height=460)
    layout["yaxis"]["title"] = dict(text="Mean score contribution",
                                    font=dict(color=SUBTLE, size=11))
    fig.update_layout(**layout, barmode="stack")
    return fig


def score_gap_waterfall_chart(rows, stats, team, top_n=5):
    # Waterfall makes it easy to see which component is responsible for the
    # gap between the selected team and the top five average
    if not rows or team not in stats:
        return _empty(f"No score gap data for {team!r}")

    top_rows = rows[:min(top_n, len(rows))]
    top_names = [r["team"] for r in top_rows]
    team_row = next((r for r in rows if r["team"] == team), None)
    if team_row is None:
        return _empty(f"No score gap data for {team!r}")

    def _component(name):
        s = stats[name]
        games = max(1, s["games"])
        pins = float(np.mean(s["pins"])) * 100.0 if s["pins"] else 0.0
        dist = float(np.mean(s["dists"])) if s["dists"] else 0.0
        move = float(np.mean(s["moves"])) if s["moves"] else 0.0
        time = float(np.mean(s["times"])) if s["times"] else 0.0
        wins = s["wins"] / games * 1000.0
        total = float(np.mean(s["scores"])) if s["scores"] else 0.0
        return {
            "Win bonus": wins,
            "Pins": pins,
            "Distance": dist,
            "Move": move,
            "Time": time,
            "Total": total,
        }

    top_parts = [_component(name) for name in top_names]
    top_avg = {
        key: float(np.mean([part[key] for part in top_parts]))
        for key in top_parts[0]
    }
    team_parts = _component(team)

    order = ["Win bonus", "Pins", "Distance", "Move", "Time"]
    deltas = [team_parts[key] - top_avg[key] for key in order]
    labels = ["Top 5 avg"] + order + [team]
    values = [top_avg["Total"]] + deltas + [team_parts["Total"]]
    measures = ["absolute"] + ["relative"] * len(order) + ["total"]

    def _delta_text(v):
        return f"{v:+.0f}"

    fig = go.Figure(go.Waterfall(
        x=labels,
        y=values,
        measure=measures,
        connector=dict(line=dict(color=GRID, width=1)),
        increasing=dict(marker=dict(color=GREEN)),
        decreasing=dict(marker=dict(color=BLUE)),
        totals=dict(marker=dict(color=HIGHLIGHT)),
        text=[f"{top_avg['Total']:.0f}"] + [_delta_text(v) for v in deltas]
             + [f"{team_parts['Total']:.0f}"],
        textposition="outside",
        textfont=dict(color=TEXT, size=12),
        hovertemplate="<b>%{x}</b><br>%{y:.1f} points<extra></extra>",
        cliponaxis=False,
    ))

    gap = team_parts["Total"] - top_avg["Total"]
    layout = _base_layout(height=470)
    layout["yaxis"]["title"] = dict(text="Mean score points",
                                      font=dict(color=SUBTLE, size=11))
    layout["xaxis"]["tickfont"] = dict(color=SUBTLE, size=11)
    fig.update_layout(**layout, showlegend=False)
    fig.add_annotation(
        x=0.99, y=0.98, xref="paper", yref="paper",
        text=f"Total gap: {gap:.0f} points",
        showarrow=False,
        font=dict(color=SUBTLE, size=12),
        align="right",
    )
    return fig


def skips_chart(rows, team):
    # Teams with fewer than five games are excluded because one bad round
    # would dominate the bar and make the chart misleading
    relevant = [r for r in rows if r["games"] >= 5]
    relevant.sort(key=lambda r: r["total_skip"])
    names = [r["team"] for r in relevant]
    skips = [r["total_skip"] for r in relevant]
    colors = [HIGHLIGHT if n == team
              else (MUTED if s == 0 else ORANGE)
              for n, s in zip(names, skips)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=skips, y=names, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[str(s) for s in skips], textposition="outside",
        textfont=dict(color=SUBTLE, size=11),
        hovertemplate="<b>%{y}</b><br>Skipped turns: %{x}<extra></extra>",
        cliponaxis=False,
    ))
    layout = _base_layout(height=max(420, 22 * len(names)), ymargin=180)
    layout["xaxis"]["title"] = dict(text="Total skipped turns across games",
                                    font=dict(color=SUBTLE, size=11))
    fig.update_layout(**layout)
    return fig


# Hex codes for the six piece colours used in the tournament data
COLOR_HEX = {
    "yellow":     "#FCD34D",
    "red":        "#F87171",
    "blue":       "#60A5FA",
    "purple":     "#A78BFA",
    "lawn green": "#86EFAC",
    "gray0":      "#9CA3AF",
}


def color_seat_chart(all_games, team):
    # Left panel shows field-wide win rate per colour to reveal any seat advantage
    # Right panel shows which colours the selected team was assigned
    by_color = defaultdict(lambda: {"games": 0, "wins": 0})
    for g in all_games:
        for name, color in g["colors"].items():
            by_color[color]["games"] += 1
            if g["winner"] == name:
                by_color[color]["wins"] += 1
    colors_sorted = sorted(by_color.keys(),
                           key=lambda c: -by_color[c]["wins"]
                                        / max(1, by_color[c]["games"]))
    win_rates = [by_color[c]["wins"] / by_color[c]["games"] * 100
                 for c in colors_sorted]
    sample_n  = [by_color[c]["games"] for c in colors_sorted]
    bar_colors = [COLOR_HEX.get(c, OTHER) for c in colors_sorted]

    team_colors = defaultdict(int)
    team_wins   = defaultdict(int)
    for g in all_games:
        c = g["colors"].get(team)
        if c is None:
            continue
        team_colors[c] += 1
        if g["winner"] == team:
            team_wins[c] += 1

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=(
                            "Tournament-wide win rate by color",
                            f"{team} — distribution of colors played",
                        ),
                        column_widths=[0.62, 0.38],
                        horizontal_spacing=0.12)
    fig.add_trace(go.Bar(
        x=win_rates, y=colors_sorted, orientation="h",
        marker=dict(color=bar_colors, line=dict(color=GRID, width=1)),
        text=[f"{w:.0f}%   (n={n})" for w, n in zip(win_rates, sample_n)],
        textposition="outside",
        textfont=dict(color=SUBTLE, size=11),
        hovertemplate="<b>%{y}</b><br>Win rate: %{x:.1f}%<extra></extra>",
        showlegend=False, cliponaxis=False,
    ), row=1, col=1)

    team_cols = sorted(team_colors.keys(),
                       key=lambda c: -team_colors[c])
    team_vals = [team_colors[c] for c in team_cols]
    team_bar_colors = [COLOR_HEX.get(c, OTHER) for c in team_cols]
    fig.add_trace(go.Bar(
        x=team_cols, y=team_vals,
        marker=dict(color=team_bar_colors, line=dict(color=GRID, width=1)),
        text=[f"{v} game{'s' if v != 1 else ''}<br>"
              f"<span style='color:{MUTED}'>{team_wins[c]} win"
              f"{'s' if team_wins[c] != 1 else ''}</span>"
              for c, v in zip(team_cols, team_vals)],
        textposition="outside",
        textfont=dict(color=SUBTLE, size=10),
        hovertemplate="<b>%{x}</b><br>%{y} game(s)<extra></extra>",
        showlegend=False, cliponaxis=False,
    ), row=1, col=2)

    layout = _base_layout(height=460, ymargin=120)
    layout["xaxis"]["title"]  = dict(text="Win rate (%)",
                                     font=dict(color=SUBTLE, size=11))
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID,
                     tickfont=dict(color=SUBTLE), row=1, col=1)
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID,
                     tickfont=dict(color=SUBTLE), row=1, col=1)
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID,
                     tickfont=dict(color=SUBTLE), row=1, col=2)
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID,
                     tickfont=dict(color=SUBTLE), row=1, col=2)
    for ann in fig.layout.annotations:
        ann.font = dict(color=TEXT, size=12, family="Inter")
    return fig


def _empty(msg):
    # Placeholder figure shown when there is not enough data to draw a real chart
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(color=SUBTLE, size=14))
    fig.update_layout(**_base_layout(height=300))
    return fig
