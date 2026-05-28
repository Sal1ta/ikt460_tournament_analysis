# Charts for the app
# Light and dark colors

from collections import defaultdict
import statistics
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Chart colors
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

BG = GRID = TEXT = SUBTLE = MUTED = OTHER = HIGHLIGHT = HIGHLIGHT_W = ""
BLUE = GREEN = TEAL = INDIGO = ORANGE = HEAT_LOW = HEAT_MID = HEAT_HIGH = HOVER_BG = ""


def set_theme(theme="light"):
    values = THEMES.get(theme, THEMES["light"])
    globals().update(values)


set_theme("light")


def _base_layout(title=None, height=520, ymargin=80):
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


def consistency_chart(stats, team):
    # Show score and consistency
    pts_names, pts_mean, pts_std, pts_color = [], [], [], []
    for name, s in stats.items():
        if len(s["scores"]) < 5:
            continue
        pts_names.append(name)
        pts_mean.append(statistics.mean(s["scores"]))
        pts_std.append(statistics.stdev(s["scores"])
                       if len(s["scores"]) > 1 else 0)
        pts_color.append(HIGHLIGHT if name == team else OTHER)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pts_mean, y=pts_std, mode="markers+text",
        marker=dict(size=[16 if n == team else 11 for n in pts_names],
                    color=pts_color,
                    line=dict(width=[2 if n == team else 0 for n in pts_names],
                              color=HIGHLIGHT_W)),
        text=[n if (n == team or len(pts_names) < 18) else "" for n in pts_names],
        textposition="top center",
        textfont=dict(color=[TEXT if n == team else SUBTLE for n in pts_names],
                      size=11),
        hovertemplate="<b>%{text}</b><br>Mean: %{x:.0f}<br>"
                      "Std-dev: %{y:.0f}<extra></extra>",
    ))
    layout = _base_layout(height=540)
    layout["xaxis"]["title"] = dict(text="Mean score (higher = better)",
                                    font=dict(color=SUBTLE, size=11))
    layout["yaxis"]["title"] = dict(text="Std-dev (lower = more consistent)",
                                    font=dict(color=SUBTLE, size=11))
    fig.update_layout(**layout)
    return fig


def timeline_chart(all_games, team):
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


def by_player_count_chart(all_games, team):
    by_n_score = defaultdict(list)
    by_n_rank  = defaultdict(list)
    by_n_win   = defaultdict(list)
    for g in all_games:
        if team not in g["scores"]:
            continue
        n = g["n_players"]
        by_n_score[n].append(g["scores"][team])
        by_n_rank[n].append(g["rank"][team])
        by_n_win[n].append(int(g["winner"] == team))
    if not by_n_score:
        return _empty(f"No games for {team!r}")

    counts = sorted(by_n_score.keys())
    means  = [np.mean(by_n_score[n]) for n in counts]
    ranks  = [np.mean(by_n_rank[n])  for n in counts]
    wins   = [np.mean(by_n_win[n]) * 100 for n in counts]
    games_n = [len(by_n_score[n]) for n in counts]
    labels = [f"{n}p<br><span style='color:{MUTED};font-size:10px'>"
              f"{g} game{'s' if g != 1 else ''}</span>"
              for n, g in zip(counts, games_n)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=means, marker=dict(color=HIGHLIGHT, line=dict(width=0)),
        text=[f"{s:.0f}" for s in means], textposition="outside",
        textfont=dict(color=TEXT, size=12),
        customdata=list(zip(ranks, wins)),
        hovertemplate="<b>%{x}</b><br>Mean score: %{y:.0f}<br>"
                      "Mean rank: %{customdata[0]:.2f}<br>"
                      "Win rate: %{customdata[1]:.0f}%<extra></extra>",
        cliponaxis=False,
    ))
    layout = _base_layout(height=440)
    layout["yaxis"]["title"] = dict(text="Mean final score",
                                    font=dict(color=SUBTLE, size=11))
    fig.update_layout(**layout)
    return fig


def rank_distribution_chart(all_games, team):
    # Show finishing rank by player count
    by_n = defaultdict(lambda: defaultdict(int))
    for g in all_games:
        if team not in g["scores"]:
            continue
        n = g["n_players"]
        by_n[n][g["rank"][team]] += 1
    if not by_n:
        return _empty(f"No games for {team!r}")

    counts = sorted(by_n.keys())
    max_rank = max(max(d.keys()) for d in by_n.values())
    colors = [GREEN, BLUE, TEAL, INDIGO, ORANGE, OTHER]

    fig = go.Figure()
    for r in range(1, max_rank + 1):
        ys = [by_n[n].get(r, 0) for n in counts]
        fig.add_trace(go.Bar(
            x=[f"{n}p" for n in counts], y=ys,
            name=f"#{r}",
            marker=dict(color=colors[(r - 1) % len(colors)],
                        line=dict(width=0)),
            hovertemplate=f"<b>#{r} finish</b><br>%{{x}}: %{{y}} game(s)"
                          "<extra></extra>",
        ))
    layout = _base_layout(height=440)
    layout["yaxis"]["title"] = dict(text="Games", font=dict(color=SUBTLE,
                                                            size=11))
    fig.update_layout(**layout, barmode="stack")
    return fig


def head_to_head_chart(all_games, team):
    # Show direct meetings
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
    # Show score parts
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
    # Show why the selected team is below the top teams
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


# More charts

COLOR_HEX = {
    "yellow":     "#FCD34D",
    "red":        "#F87171",
    "blue":       "#60A5FA",
    "purple":     "#A78BFA",
    "lawn green": "#86EFAC",
    "gray0":      "#9CA3AF",
}


def color_seat_chart(all_games, team):
    # Show colour wins and selected team colours
    # Field colour wins
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

    # Selected team colours
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


def strength_of_schedule_chart(all_games, rows, team):
    # Show average opponent strength
    rank_lookup = {r["team"]: i + 1 for i, r in enumerate(rows)}
    by_team = defaultdict(list)
    for g in all_games:
        members = list(g["scores"].keys())
        for m in members:
            for opp in members:
                if opp == m:
                    continue
                if opp in rank_lookup:
                    by_team[m].append(rank_lookup[opp])
    rows_sorted = sorted(
        [(t, float(np.mean(rs))) for t, rs in by_team.items()
         if len(rs) >= 5],
        key=lambda kv: kv[1])     # lower = harder schedule first
    names = [t for t, _ in rows_sorted]
    means = [m for _, m in rows_sorted]
    colors = [HIGHLIGHT if n == team else OTHER for n in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=means, y=names, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{m:.1f}" for m in means],
        textposition="outside",
        textfont=dict(color=SUBTLE, size=11),
        hovertemplate="<b>%{y}</b><br>Mean opponent rank: %{x:.2f}"
                      "<extra></extra>",
        cliponaxis=False,
    ))
    field_mean = float(np.mean(means))
    fig.add_vline(x=field_mean, line_dash="dash", line_color=SUBTLE,
                  line_width=1,
                  annotation_text=f"field mean {field_mean:.1f}",
                  annotation_position="top",
                  annotation_font_color=SUBTLE,
                  annotation_font_size=10)
    layout = _base_layout(height=max(420, 22 * len(names)), ymargin=180)
    layout["xaxis"]["title"] = dict(
        text="Mean opponent tournament-rank  ·  lower = harder schedule",
        font=dict(color=SUBTLE, size=11))
    fig.update_layout(**layout)
    return fig


def speed_vs_rank_chart(stats, team):
    # Show speed against rank
    pts_name, pts_time, pts_rank, pts_games = [], [], [], []
    for name, s in stats.items():
        if len(s["scores"]) < 5 or not s["times"]:
            continue
        # Estimate time taken from time score
        # Only used for chart ranking
        mean_t = 100 - float(np.mean(s["times"]))
        pts_name.append(name)
        pts_time.append(max(0.0, mean_t))
        pts_rank.append(float(np.mean(s["ranks"])))
        pts_games.append(len(s["scores"]))

    colors = [HIGHLIGHT if n == team else OTHER for n in pts_name]
    sizes  = [16 if n == team else 11 for n in pts_name]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pts_time, y=pts_rank, mode="markers+text",
        marker=dict(size=sizes, color=colors,
                    line=dict(width=[2 if n == team else 0 for n in pts_name],
                              color=HIGHLIGHT_W)),
        text=[n if (n == team or len(pts_name) < 16) else "" for n in pts_name],
        textposition="top center",
        textfont=dict(color=[TEXT if n == team else SUBTLE for n in pts_name],
                      size=11),
        customdata=pts_games,
        hovertemplate="<b>%{text}</b><br>Mean time: %{x:.1f}s<br>"
                      "Mean rank: %{y:.2f}<br>"
                      "Games: %{customdata}<extra></extra>",
    ))
    # Add trend line
    if len(pts_time) > 2:
        slope, intercept = np.polyfit(pts_time, pts_rank, 1)
        xs = np.linspace(min(pts_time), max(pts_time), 50)
        ys = slope * xs + intercept
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines",
            line=dict(color=SUBTLE, dash="dot", width=1),
            hoverinfo="skip", showlegend=False,
        ))

    layout = _base_layout(height=520)
    layout["xaxis"]["title"] = dict(
        text="Mean time taken per game (s) — lower = faster agent",
        font=dict(color=SUBTLE, size=11))
    layout["yaxis"]["title"] = dict(
        text="Mean rank (1 = best)",
        font=dict(color=SUBTLE, size=11))
    layout["yaxis"]["autorange"] = "reversed"   # rank 1 at top
    fig.update_layout(**layout, showlegend=False)
    return fig


def head_to_head_matrix_chart(all_games, rows, team):
    # Build direct match matrix
    rank_lookup = {r["team"]: i + 1 for i, r in enumerate(rows)}
    eligible = [r["team"] for r in rows if r["games"] >= 5]
    ordered = sorted(eligible, key=lambda t: rank_lookup[t])
    n = len(ordered)

    # Count direct wins for each team pair
    pair = defaultdict(lambda: {"row_higher": 0, "col_higher": 0})
    for g in all_games:
        members = [m for m in g["scores"] if m in rank_lookup]
        for a in members:
            for b in members:
                if a == b:
                    continue
                if g["rank"][a] < g["rank"][b]:
                    pair[(a, b)]["row_higher"] += 1

    z      = [[None] * n for _ in range(n)]
    text   = [[""]   * n for _ in range(n)]
    hover  = [[""]   * n for _ in range(n)]
    for i, a in enumerate(ordered):
        for j, b in enumerate(ordered):
            if a == b:
                z[i][j] = None
                text[i][j] = ""
                hover[i][j] = ""
                continue
            wins  = pair[(a, b)]["row_higher"]
            losses = pair[(b, a)]["row_higher"]
            total = wins + losses
            if total == 0:
                z[i][j] = None
                text[i][j] = "·"
                hover[i][j] = f"{a} vs {b}<br>never met"
                continue
            share = wins / total
            z[i][j] = share
            text[i][j] = f"{wins}-{losses}"
            hover[i][j] = (f"<b>{a}</b> vs <b>{b}</b><br>"
                           f"{a} higher: {wins}<br>"
                           f"{b} higher: {losses}<br>"
                           f"Total meetings: {total}")

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=z, x=ordered, y=ordered,
        colorscale=[
            [0.0,  HEAT_LOW],
            [0.5,  HEAT_MID],
            [1.0,  HEAT_HIGH],
        ],
        zmin=0.0, zmax=1.0,
        hoverongaps=False,
        text=text, texttemplate="%{text}",
        textfont=dict(size=10, color=TEXT, family="Inter"),
        customdata=hover, hovertemplate="%{customdata}<extra></extra>",
        xgap=2, ygap=2,
        showscale=True,
        colorbar=dict(
            title=dict(text="Row team's<br>win share",
                       font=dict(color=SUBTLE, size=11)),
            tickfont=dict(color=SUBTLE),
            tickvals=[0.0, 0.5, 1.0],
            ticktext=["row<br>loses", "even", "row<br>dominates"],
            len=0.6, thickness=14,
            outlinecolor=GRID, outlinewidth=0,
            bgcolor="rgba(0,0,0,0)",
            x=1.02,
        ),
    ))

    layout = _base_layout(height=max(640, 28 * n), ymargin=200)
    fig.update_layout(**layout)
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=11, color=SUBTLE),
                     side="bottom")
    fig.update_yaxes(tickfont=dict(size=11, color=SUBTLE),
                     autorange="reversed")     # rank 1 at top

    if team in ordered:
        idx = ordered.index(team)
        fig.add_shape(type="rect",
                      x0=-0.5, x1=n - 0.5,
                      y0=idx - 0.5, y1=idx + 0.5,
                      line=dict(color=HIGHLIGHT_W, width=2),
                      fillcolor="rgba(37,99,235,0.06)",
                      layer="above")
        fig.add_shape(type="rect",
                      x0=idx - 0.5, x1=idx + 0.5,
                      y0=-0.5, y1=n - 0.5,
                      line=dict(color=HIGHLIGHT_W, width=2),
                      fillcolor="rgba(37,99,235,0.06)",
                      layer="above")
    return fig


def _empty(msg):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(color=SUBTLE, size=14))
    fig.update_layout(**_base_layout(height=300))
    return fig
