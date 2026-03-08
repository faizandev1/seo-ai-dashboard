import os
import json
import pandas as pd
import plotly.express as px
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def load_gsc_queries():
    data = load_json('data/gsc/queries.json')
    rows = data.get('queries', [])
    fetched_at = data.get('fetched_at', '')
    records = []
    for row in rows:
        keys = row.get('keys', [])
        records.append({
            'keyword': keys[0] if keys else '',
            'clicks': row.get('clicks', 0),
            'impressions': row.get('impressions', 0),
            'ctr': round(row.get('ctr', 0) * 100, 2),
            'position': round(row.get('position', 0), 1)
        })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['keyword','clicks','impressions','ctr','position'])
    return df, fetched_at

def load_gsc_pages():
    data = load_json('data/gsc/pages.json')
    rows = data.get('pages', [])
    records = []
    for row in rows:
        keys = row.get('keys', [])
        records.append({
            'page': keys[0] if keys else '',
            'clicks': row.get('clicks', 0),
            'impressions': row.get('impressions', 0),
            'ctr': round(row.get('ctr', 0) * 100, 2),
            'position': round(row.get('position', 0), 1)
        })
    return pd.DataFrame(records) if records else pd.DataFrame(columns=['page','clicks','impressions','ctr','position'])

def load_ga4_channels():
    data = load_json('data/ga4/channels.json')
    channels = data.get('channels', [])
    records = []
    for ch in channels:
        records.append({
            'channel': ch.get('channel', ''),
            'sessions': int(ch.get('sessions', 0)),
            'users': int(ch.get('users', 0)),
            'bounce_rate': round(float(ch.get('bounce_rate', 0)) * 100, 2)
        })
    return pd.DataFrame(records) if records else pd.DataFrame(columns=['channel','sessions','users','bounce_rate'])

def scale_by_days(df, days):
    if df.empty or days == 90:
        return df
    ratio = days / 90
    df = df.copy()
    for col in ['clicks', 'impressions']:
        if col in df.columns:
            df[col] = (df[col] * ratio).round(0).astype(int)
    return df

@app.route('/')
def dashboard():
    site = os.getenv('GSC_PROPERTY_URL', 'Your Site')
    days = int(request.args.get('days', 90))
    if days not in [1, 3, 7, 28, 90]:
        days = 90

    label_map = {1:'Today', 3:'Last 3 Days', 7:'Last 7 Days', 28:'Last 28 Days', 90:'Last 90 Days'}
    selected_label = label_map[days]

    queries_df, fetched_at = load_gsc_queries()
    pages_df    = load_gsc_pages()
    channels_df = load_ga4_channels()

    queries_df = scale_by_days(queries_df, days)
    pages_df   = scale_by_days(pages_df, days)

    try:
        ft = datetime.fromisoformat(fetched_at)
        fetched_str = ft.strftime('%d %b %Y %H:%M')
    except:
        fetched_str = 'Not fetched yet'

    total_clicks      = int(queries_df['clicks'].sum())         if not queries_df.empty  else 0
    total_impressions = int(queries_df['impressions'].sum())    if not queries_df.empty  else 0
    avg_position      = round(queries_df['position'].mean(), 1) if not queries_df.empty  else 0
    avg_ctr           = round(queries_df['ctr'].mean(), 2)      if not queries_df.empty  else 0
    total_sessions    = int(channels_df['sessions'].sum())      if not channels_df.empty else 0
    total_keywords    = len(queries_df)

    page2_df = queries_df[(queries_df['position'] >= 11) & (queries_df['position'] <= 20)].sort_values('impressions', ascending=False).head(10) if not queries_df.empty else pd.DataFrame()
    ctr_df   = queries_df[(queries_df['impressions'] > 10) & (queries_df['ctr'] < 2)].sort_values('impressions', ascending=False).head(10)    if not queries_df.empty else pd.DataFrame()
    top3_df  = queries_df[queries_df['position'] <= 3].sort_values('clicks', ascending=False).head(10) if not queries_df.empty else pd.DataFrame()

    dark = {'plot_bgcolor':'#1e1e2e','paper_bgcolor':'#1e1e2e','font_color':'white','title_font_color':'#4a9eff'}

    top_keywords_chart = ""
    if not queries_df.empty:
        top10 = queries_df.sort_values('clicks', ascending=False).head(10)
        fig = px.bar(top10, x='keyword', y='clicks',
                     title=f'Top 10 Keywords — {selected_label}',
                     color='clicks', color_continuous_scale='Blues')
        fig.update_layout(**dark, xaxis_tickangle=-30)
        top_keywords_chart = fig.to_html(full_html=False)

    channels_chart = ""
    if not channels_df.empty:
        fig2 = px.pie(channels_df, values='sessions', names='channel',
                      title='Traffic by Channel',
                      color_discrete_sequence=px.colors.sequential.Blues_r)
        fig2.update_layout(**dark)
        channels_chart = fig2.to_html(full_html=False)

    position_chart = ""
    if not queries_df.empty:
        bins   = [0, 3, 10, 20, 50, 100]
        labels = ['Top 3','Page 1 (4-10)','Page 2 (11-20)','Page 3-5','Beyond']
        qdf = queries_df.copy()
        qdf['position_group'] = pd.cut(qdf['position'], bins=bins, labels=labels)
        pos_counts = qdf['position_group'].value_counts().reset_index()
        pos_counts.columns = ['Position','Count']
        fig3 = px.bar(pos_counts, x='Position', y='Count',
                      title='Keyword Position Distribution',
                      color='Count', color_continuous_scale='Blues')
        fig3.update_layout(**dark)
        position_chart = fig3.to_html(full_html=False)

    ctr_chart = ""
    if not queries_df.empty:
        sample = queries_df[queries_df['impressions'] > 5].head(80)
        fig4 = px.scatter(sample, x='position', y='ctr',
                          size='impressions', hover_data=['keyword'],
                          title='CTR vs Position',
                          color='ctr', color_continuous_scale='Blues')
        fig4.update_layout(**dark)
        ctr_chart = fig4.to_html(full_html=False)

    def table_rows(df, cols, badge_col=None):
        if df is None or df.empty:
            return f'<tr><td colspan="{len(cols)+1}" style="text-align:center;color:#555;padding:20px">No data — run python main.py</td></tr>'
        out = ""
        for _, row in df.iterrows():
            out += "<tr>"
            for c in cols:
                val = row.get(c, '')
                if isinstance(val, float) and val == int(val):
                    val = int(val)
                cell = str(val)
                if c in ['keyword','page']:
                    cell = cell[:55] + ('...' if len(str(val)) > 55 else '')
                out += f"<td>{cell}</td>"
            if badge_col:
                pos = row.get(badge_col, 99)
                if pos <= 3:
                    b = ('badge-blue','Top 3')
                elif pos <= 10:
                    b = ('badge-green','Page 1')
                else:
                    b = ('badge-orange','Page 2+')
                out += f'<td><span class="badge {b[0]}">{b[1]}</span></td>'
            out += "</tr>"
        return out

    filter_buttons = ""
    for d, lbl in label_map.items():
        active = 'active' if d == days else ''
        filter_buttons += f'<a href="/?days={d}" class="filter-btn {active}">{lbl}</a>'

    note_html = ''
    if days < 90:
        note_html = f'<div class="note">Showing estimated data for <strong>{selected_label}</strong>. GSC API returns aggregated 90-day data. Run <strong>python main.py</strong> daily for freshest numbers.</div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
<title>SEO Dashboard — {site}</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:#0a0a14;color:#e0e0e0}}
.header{{background:linear-gradient(135deg,#12122a,#1e1e3a);padding:18px 30px;border-bottom:2px solid #4a9eff;display:flex;justify-content:space-between;align-items:center}}
.header h1{{color:#4a9eff;font-size:22px;font-weight:700}}
.header p{{color:#555;font-size:12px;margin-top:3px}}
.live-badge{{background:#0d2a0d;color:#4caf50;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:bold;border:1px solid #4caf50}}
.filter-bar{{background:#0d0d1f;padding:12px 30px;border-bottom:1px solid #1a1a2e;display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.filter-label{{color:#555;font-size:12px;margin-right:4px;white-space:nowrap}}
.filter-btn{{padding:6px 14px;border-radius:20px;font-size:12px;text-decoration:none;color:#888;border:1px solid #2a2a44;background:#12122a;transition:all .2s;white-space:nowrap}}
.filter-btn:hover{{border-color:#4a9eff;color:#4a9eff}}
.filter-btn.active{{background:#4a9eff;color:white;border-color:#4a9eff;font-weight:bold}}
.fetched-info{{margin-left:auto;color:#444;font-size:11px;white-space:nowrap}}
.container{{padding:20px 30px}}
.stats-grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:20px}}
.stat-card{{background:linear-gradient(135deg,#12122a,#1a1a2e);border:1px solid #2a2a44;border-radius:12px;padding:16px;text-align:center;transition:transform .2s,border-color .2s}}
.stat-card:hover{{transform:translateY(-3px);border-color:#4a9eff}}
.stat-card .icon{{font-size:20px;margin-bottom:5px}}
.stat-card .number{{font-size:26px;font-weight:bold;color:#4a9eff;margin:4px 0}}
.stat-card .label{{color:#555;font-size:11px}}
.charts-2big{{display:grid;grid-template-columns:3fr 2fr;gap:14px;margin-bottom:14px}}
.charts-2{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}}
.chart-box{{background:#12122a;border:1px solid #2a2a44;border-radius:12px;padding:12px}}
.section-title{{color:#4a9eff;font-size:14px;font-weight:600;margin:20px 0 10px;padding-bottom:6px;border-bottom:1px solid #1a1a2e;display:flex;align-items:center;gap:8px}}
.tag{{background:#0d1f3a;color:#4a9eff;font-size:10px;padding:2px 8px;border-radius:10px;border:1px solid #2a3a5a}}
.table-box{{background:#12122a;border:1px solid #2a2a44;border-radius:12px;padding:16px;margin-bottom:14px;overflow-x:auto}}
table{{width:100%;border-collapse:collapse}}
th{{background:#1a1a2e;color:#4a9eff;padding:10px 12px;text-align:left;font-size:11px;font-weight:600;letter-spacing:.4px;text-transform:uppercase}}
td{{padding:9px 12px;border-bottom:1px solid #1a1a2e;font-size:12px;color:#bbb}}
tr:hover td{{background:#1a1a2e}}
tr:last-child td{{border-bottom:none}}
.badge{{padding:2px 8px;border-radius:10px;font-size:10px;font-weight:bold}}
.badge-green{{background:#0d2a0d;color:#4caf50;border:1px solid #2a5a2a}}
.badge-blue{{background:#0d1f3a;color:#4a9eff;border:1px solid #2a3a5a}}
.badge-orange{{background:#2a1a0d;color:#ff9800;border:1px solid #5a3a0d}}
.refresh-btn{{background:transparent;color:#4a9eff;border:1px solid #4a9eff;padding:6px 16px;border-radius:20px;cursor:pointer;font-size:12px;text-decoration:none;transition:all .2s}}
.refresh-btn:hover{{background:#4a9eff;color:white}}
.note{{background:#12201a;border:1px solid #1a3a24;border-radius:8px;padding:10px 16px;font-size:11px;color:#666;margin-bottom:16px}}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>SEO AI Dashboard</h1>
    <p>{site}</p>
  </div>
  <div style="display:flex;align-items:center;gap:12px">
    <span class="live-badge">LIVE</span>
    <a href="/?days={days}" class="refresh-btn">Refresh</a>
  </div>
</div>

<div class="filter-bar">
  <span class="filter-label">Date Range:</span>
  {filter_buttons}
  <span class="fetched-info">Last fetched: {fetched_str} &nbsp;|&nbsp; <strong>python main.py</strong> to update</span>
</div>

<div class="container">
  {note_html}

  <div class="stats-grid">
    <div class="stat-card"><div class="icon">🖱️</div><div class="number">{total_clicks:,}</div><div class="label">Clicks</div></div>
    <div class="stat-card"><div class="icon">👁️</div><div class="number">{total_impressions:,}</div><div class="label">Impressions</div></div>
    <div class="stat-card"><div class="icon">📍</div><div class="number">{avg_position}</div><div class="label">Avg Position</div></div>
    <div class="stat-card"><div class="icon">📊</div><div class="number">{avg_ctr}%</div><div class="label">Avg CTR</div></div>
    <div class="stat-card"><div class="icon">👥</div><div class="number">{total_sessions:,}</div><div class="label">GA4 Sessions</div></div>
    <div class="stat-card"><div class="icon">🔑</div><div class="number">{total_keywords:,}</div><div class="label">Keywords</div></div>
  </div>

  <div class="charts-2big">
    <div class="chart-box">{top_keywords_chart or '<p style="color:#444;padding:40px;text-align:center">No data — run python main.py</p>'}</div>
    <div class="chart-box">{channels_chart or '<p style="color:#444;padding:40px;text-align:center">No GA4 data yet</p>'}</div>
  </div>

  <div class="charts-2">
    <div class="chart-box">{position_chart or ''}</div>
    <div class="chart-box">{ctr_chart or ''}</div>
  </div>

  <div class="section-title">Page 2 Keywords — Quick Wins <span class="tag">Position 11–20</span></div>
  <div class="table-box">
    <table>
      <tr><th>Keyword</th><th>Position</th><th>Impressions</th><th>Clicks</th><th>CTR %</th></tr>
      {table_rows(page2_df, ['keyword','position','impressions','clicks','ctr'])}
    </table>
  </div>

  <div class="section-title">High Impressions — Low CTR <span class="tag">Fix Meta Titles</span></div>
  <div class="table-box">
    <table>
      <tr><th>Keyword</th><th>Impressions</th><th>Clicks</th><th>CTR %</th><th>Position</th></tr>
      {table_rows(ctr_df, ['keyword','impressions','clicks','ctr','position'])}
    </table>
  </div>

  <div class="section-title">Top 3 Position Keywords <span class="tag">Already Winning</span></div>
  <div class="table-box">
    <table>
      <tr><th>Keyword</th><th>Clicks</th><th>Impressions</th><th>CTR %</th><th>Position</th><th>Status</th></tr>
      {table_rows(top3_df, ['keyword','clicks','impressions','ctr','position'], badge_col='position')}
    </table>
  </div>

  <div class="section-title">Top Pages <span class="tag">All Pages</span></div>
  <div class="table-box">
    <table>
      <tr><th>Page</th><th>Clicks</th><th>Impressions</th><th>CTR %</th><th>Position</th><th>Status</th></tr>
      {table_rows(pages_df.head(15), ['page','clicks','impressions','ctr','position'], badge_col='position')}
    </table>
  </div>

</div>
</body>
</html>"""
    return html

if __name__ == "__main__":
    print("=" * 50)
    print("SEO DASHBOARD STARTING...")
    print("Open browser: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    app.run(debug=True, port=5000)
