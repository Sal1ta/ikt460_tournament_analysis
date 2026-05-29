# Streamlit dashboard for the IKT460 Chinese Checkers tournament results

import csv
import io
import zipfile
import streamlit as st

import analysis as at
import charts as sc


# Page setup
st.set_page_config(
    page_title="IKT460 Tournament Analysis",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme setup
THEME_OPTIONS = ("Report white", "System", "Dark")
theme_choice = st.sidebar.selectbox("Theme", THEME_OPTIONS, index=0)
chart_theme = "dark" if theme_choice == "Dark" else "light"

LIGHT_THEME = {
    "page":          "#F8FAFC",   # light page
    "sidebar":       "#F0FDFA",   # soft sidebar tint
    "card":          "#FFFFFF",   # pure white
    "border":        "#CCFBF1",   # soft border
    "text":          "#0F172A",   # slate-900
    "subtle":        "#475569",   # slate-600
    "muted":         "#64748B",   # slate-500
    "button_hover":  "#CCFBF1",   # hover highlight
    "accent":        "#0D9488",   # main accent
    "positive":      "#10B981",   # positive green
    "warning":       "#F59E0B",   # warning color
}
DARK_THEME = {
    "page": "#0B1220",
    "sidebar": "#0F172A",
    "card": "#111827",
    "border": "#243044",
    "text": "#E5E7EB",
    "subtle": "#CBD5E1",
    "muted": "#94A3B8",
    "button_hover": "#1E293B",
    "accent": "#60A5FA",
    "positive": "#34D399",
    "warning": "#FBBF24",
}


def _css_vars(values):
    return "\n".join(f"    --{key}: {value};" for key, value in values.items())


if theme_choice == "Dark":
    root_vars = _css_vars(DARK_THEME)
    system_override = ""
elif theme_choice == "System":
    root_vars = _css_vars(LIGHT_THEME)
    system_override = (
        "@media (prefers-color-scheme: dark) {\n"
        "  :root {\n"
        f"{_css_vars(DARK_THEME)}\n"
        "  }\n"
        "}\n"
    )
else:
    root_vars = _css_vars(LIGHT_THEME)
    system_override = ""

# CSS styling
st.markdown(f"""
<style>
@import url('https://rsms.me/inter/inter.css');

:root {{
{root_vars}
}}
{system_override}

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

.stApp {{
    background: var(--page);
    color: var(--text);
}}

.block-container {{
    padding-top: 1.1rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}}

h1, h2, h3 {{ letter-spacing: 0; color: var(--text); }}
h1 {{ font-weight: 700 !important; font-size: 1.75rem !important; }}
h2 {{ font-weight: 600 !important; font-size: 1.25rem !important;
     margin-top: 1.5rem !important; }}
h3 {{ font-weight: 600 !important; font-size: 1.0rem !important; }}

.caption {{
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--muted);
    margin-bottom: 0.25rem;
}}

.stat-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.6rem;
}}
.stat-value {{
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
    margin: 0;
}}
.stat-sub {{
    font-size: 0.85rem;
    color: var(--subtle);
    margin-top: 0.2rem;
}}
.stat-delta-neg {{ color: var(--warning); font-weight: 500; }}
.stat-delta-pos {{ color: var(--positive); font-weight: 500; }}

[data-testid="stSidebar"] {{
    background: var(--sidebar);
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {{
    color: var(--text) !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid var(--border);
}}
.stTabs [data-baseweb="tab"] {{
    padding: 0.6rem 0.9rem;
    font-weight: 500;
    color: var(--subtle);
    background: transparent;
    border: none;
}}
.stTabs [aria-selected="true"] {{
    color: var(--text) !important;
    border-bottom: 2px solid var(--accent) !important;
}}
.stTabs [data-baseweb="tab-list"] button {{
    background: transparent !important;
    color: var(--subtle) !important;
    border: none !important;
}}
.stTabs [data-baseweb="tab-list"] button:hover {{
    background: var(--button_hover) !important;
    color: var(--text) !important;
}}
.stTabs [data-baseweb="tab-list"] button svg {{
    fill: var(--text) !important;
}}
.stTabs button[aria-label] {{
    background: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}}

.stSelectbox > div > div {{
    border-radius: 8px !important;
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
}}
[data-baseweb="select"] > div {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}}
[data-baseweb="select"] div,
[data-baseweb="select"] span,
[data-baseweb="select"] svg,
[data-baseweb="select"] input {{
    color: var(--text) !important;
    fill: var(--text) !important;
}}
[data-baseweb="select"] [role="combobox"] {{
    background: var(--card) !important;
}}
[data-baseweb="input"] input {{
    color: var(--text) !important;
}}
[data-baseweb="popover"] > div {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
}}
[data-baseweb="menu"] {{
    background: var(--card) !important;
}}
[data-baseweb="menu"] li {{
    color: var(--text) !important;
}}
[data-baseweb="menu"] li:hover {{
    background: var(--button_hover) !important;
}}

.stButton > button, .stDownloadButton > button {{
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--card);
    color: var(--text);
    padding: 0.45rem 0.9rem;
    font-weight: 500;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: var(--accent);
    background: var(--button_hover);
}}

[data-testid="stImage"] img {{
    border-radius: 8px;
    border: 1px solid var(--border);
}}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeaderActionElements"],
.stDeployButton,
button[title="Deploy"] {{
    display: none !important;
}}
#MainMenu {{ visibility: hidden; }}
footer    {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}
</style>
""", unsafe_allow_html=True)


def fig_to_png_bytes(fig, width=1800, height=None, scale=2):
    # Render a Plotly figure to PNG bytes
    h = height or fig.layout.height or 600
    return fig.to_image(format="png", width=width, height=h, scale=scale)


# Load tournament data
@st.cache_data(show_spinner=False)
def load_data():
    data_dir = at.DEFAULT_DATA
    at.ensure_downloaded(data_dir)
    games = []
    for round_no in range(1, at.NUM_ROUNDS + 1):
        path = data_dir / f"round{round_no}.txt"
        if path.exists():
            games.extend(at.parse_round(path, round_no))
    stats = at.aggregate(games)
    rows = at.leaderboard(stats)
    return games, stats, rows


all_games, stats, rows = load_data()
teams = [r["team"] for r in rows]
sc.set_theme(chart_theme)


# Sidebar
with st.sidebar:
    st.markdown('<div class="caption">Tournament</div>', unsafe_allow_html=True)
    st.markdown("## IKT460 Chinese Checkers")
    st.caption(f"May 2026 · {len(teams)} teams · {len(all_games)} games")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="caption">Highlight team</div>', unsafe_allow_html=True)
    default_team = at.DEFAULT_TEAM if at.DEFAULT_TEAM in teams else teams[0]
    team = st.selectbox(
        "Team",
        teams,
        index=teams.index(default_team),
        label_visibility="collapsed",
    )


# Selected team summary
rank = next(i for i, r in enumerate(rows, 1) if r["team"] == team)
selected = rows[rank - 1]
best_score = rows[0]["mean_score"] if rows else 0
gap = selected["mean_score"] - best_score


def _team_slug(name):
    # Make a safe file name from a team name
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")


def stat_card(label, value, sub=None, delta=None):
    # Show one summary value in a small card
    delta_html = ""
    if delta:
        css = "stat-delta-pos" if delta.startswith("+") else "stat-delta-neg"
        delta_html = f'<div class="stat-sub {css}">{delta}</div>'
    sub_html = f'<div class="stat-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'''<div class="stat-card">
            <div class="caption">{label}</div>
            <p class="stat-value">{value}</p>
            {delta_html}{sub_html}
        </div>''',
        unsafe_allow_html=True,
    )


st.title(team)
st.caption(
    f"Rank #{rank} of {len(rows)} · {selected['games']} games played · "
    f"{selected['wins']} wins"
)

stat_cols = st.columns(5)
with stat_cols[0]:
    stat_card("Rank", f"#{rank}", f"of {len(rows)} teams")
with stat_cols[1]:
    stat_card("Mean score", f"{selected['mean_score']:.0f}",
              delta=f"{gap:.0f} from #1")
with stat_cols[2]:
    stat_card("Win rate", f"{selected['win_rate'] * 100:.0f}%",
              f"{selected['wins']} of {selected['games']} games")
with stat_cols[3]:
    stat_card("Mean pins home", f"{selected['mean_pins'] * 10:.1f}",
              "out of 10")
with stat_cols[4]:
    skip_text = "no skipped turns" if selected["total_skip"] == 0 else "skipped turns"
    stat_card("Skipped turns", f"{selected['total_skip']}", skip_text)

st.markdown("<br>", unsafe_allow_html=True)

chart_specs = [
    ("Components", "Where the score came from for the top teams and you",
     "components", lambda: sc.components_chart(stats, team)),
    ("Gap to top 5", "Point gap from the top 5 average, split by score part",
     "score_gap", lambda: sc.score_gap_waterfall_chart(rows, stats, team)),
    ("Timeline", f"{team}'s score in each game, with stars for wins", "timeline",
     lambda: sc.timeline_chart(all_games, team)),
    ("Head-to-head", f"Teams {team} finished above or below in the same games",
     "head_to_head", lambda: sc.head_to_head_chart(all_games, team)),
    ("Color seat", "Win rate by colour and the colours drawn by the selected team",
     "color_seat", lambda: sc.color_seat_chart(all_games, team)),
    ("Skips", "Total skipped turns for each team", "skips",
     lambda: sc.skips_chart(rows, team)),
]

tabs = st.tabs(["Leaderboard"] + [name for name, _, _, _ in chart_specs])


# Store charts for the zip export
if ("charts_for_zip" not in st.session_state
        or st.session_state.get("zip_team") != team):
    st.session_state.charts_for_zip = {}
    st.session_state.zip_team = team


def plot(fig, slug):
    # Show chart and remember it for export
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False, "displaylogo": False},
                    key=f"chart_{slug}_{team}")
    st.session_state.charts_for_zip[slug] = fig


# Leaderboard table
with tabs[0]:
    st.caption("Leaderboard for every team")
    leader_data = [{
        "Rank": i,
        "Team": ("* " if r["team"] == team else "") + r["team"],
        "Mean score": round(r["mean_score"], 1),
        "Wins": r["wins"],
        "Win rate": r["win_rate"],
        "Mean pins": r["mean_pins"] * 10,
        "Skipped": r["total_skip"],
    } for i, r in enumerate(rows, 1)]

    st.dataframe(
        leader_data,
        hide_index=True,
        use_container_width=True,
        height=min(640, 35 * (len(leader_data) + 1) + 4),
        column_config={
            "Rank": st.column_config.NumberColumn(width="small"),
            "Team": st.column_config.TextColumn(width="medium"),
            "Mean score": st.column_config.ProgressColumn(
                "Mean score", format="%.0f", min_value=0,
                max_value=int(max(r["mean_score"] for r in rows) * 1.05),
            ),
            "Wins": st.column_config.NumberColumn(width="small"),
            "Win rate": st.column_config.ProgressColumn(
                "Win rate", format="percent", min_value=0,
                max_value=1.0, width="medium",
            ),
            "Mean pins": st.column_config.ProgressColumn(
                "Pins home", format="%.1f / 10", min_value=0, max_value=10,
            ),
            "Skipped": st.column_config.NumberColumn(width="small"),
        },
    )

    _leader_csv = io.StringIO()
    _writer = csv.DictWriter(_leader_csv, fieldnames=list(leader_data[0].keys()))
    _writer.writeheader()
    _writer.writerows(leader_data)
    st.download_button("Download leaderboard as CSV", _leader_csv.getvalue(),
                       "leaderboard.csv", "text/csv", key="dl_leaderboard_csv")


for tab, (_, caption, slug, make_chart) in zip(tabs[1:], chart_specs):
    with tab:
        st.caption(caption)
        plot(make_chart(), slug)


# Export plots
# Make a zip with every chart and the leaderboard csv
def _build_zip():
    # Ensure every chart is rendered even if its tab was never visited
    for _, _, slug, make_chart in chart_specs:
        if slug not in st.session_state.charts_for_zip:
            st.session_state.charts_for_zip[slug] = make_chart()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        slug = _team_slug(team)
        for chart_slug, fig in st.session_state.charts_for_zip.items():
            try:
                png = fig_to_png_bytes(fig)
                zf.writestr(f"charts/{chart_slug}_{slug}.png", png)
            except Exception as e:
                zf.writestr(f"charts/{chart_slug}_{slug}.ERROR.txt",
                            f"PNG export failed: {e}\n")
        # Add leaderboard CSV to the zip
        leader_csv = io.StringIO()
        w = csv.DictWriter(leader_csv, fieldnames=list(leader_data[0].keys()))
        w.writeheader(); w.writerows(leader_data)
        zf.writestr("leaderboard.csv", leader_csv.getvalue())
    buf.seek(0)
    return buf.getvalue()


with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="caption">Export plots</div>',
                unsafe_allow_html=True)

    # Build the zip only when the button is clicked
    build_clicked = st.button(
        f"Build PNG zip for {team}",
        key="build_zip_btn",
        use_container_width=True,
        type="primary",
    )
    if build_clicked:
        with st.spinner(f"Rendering {len(st.session_state.charts_for_zip)} "
                        "charts as PNG…"):
            try:
                st.session_state.zip_bytes = _build_zip()
                st.session_state.zip_team_built = team
            except Exception as e:
                st.error(f"Build failed: {e}")
                st.session_state.zip_bytes = None

    have_zip = (st.session_state.get("zip_bytes")
                and st.session_state.get("zip_team_built") == team)
    if have_zip:
        st.download_button(
            label="⬇  Download .zip",
            data=st.session_state.zip_bytes,
            file_name=f"tournamentanalysis_{_team_slug(team)}.zip",
            mime="application/zip",
            key="dl_zip_all",
            use_container_width=True,
        )
        st.caption(f"{len(st.session_state.charts_for_zip)} charts + "
                   "leaderboard CSV  ·  "
                   f"~{len(st.session_state.zip_bytes) // 1024} KB")
    else:
        st.caption("Click Build PNG zip first, then download the zip file")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="caption">Source code</div>', unsafe_allow_html=True)
    st.markdown(
        "[github.com/Sal1ta/ikt460_tournament_analysis]"
        "(https://github.com/Sal1ta/ikt460_tournament_analysis)",
        unsafe_allow_html=False,
    )
