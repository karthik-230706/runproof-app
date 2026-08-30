from html import escape
import json

def render_report(analysis,passport):
    score=analysis['score']; issues=analysis['issues']; ver=analysis.get('verification',{})
    rows=''.join(f"<tr><td>{escape(k.replace('_',' ').title())}</td><td>{escape(str(v.get('status')))}</td><td>{v.get('weight')}</td></tr>" for k,v in score['checks'].items())
    issue_html=''.join(f"<div class='issue {escape(i['severity'])}'><h3>{escape(i['title'])}</h3><p><b>Why:</b> {escape(i['why'])}</p><p><b>Fix:</b> {escape(i['fix'])}</p></div>" for i in issues) or '<p>No issues found.</p>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>RunProof Report</title><style>
    body{{font-family:Inter,Arial,sans-serif;background:#07101d;color:#e5eefb;margin:0;padding:40px}}main{{max-width:980px;margin:auto}}.card{{background:#101827;border:1px solid #26344a;border-radius:18px;padding:22px;margin:16px 0}}h1{{font-size:42px}}.score{{font-size:48px;color:#4ade80;font-weight:900}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid #26344a;text-align:left}}.issue{{border-left:4px solid #f59e0b;padding:12px 16px;background:#111827;margin:10px 0;border-radius:8px}}.critical,.high{{border-left-color:#ef4444}}code{{color:#93c5fd}}</style></head><body><main>
    <h1>RunProof Verification Report</h1><p>Project: <b>{escape(analysis['scan']['project_name'])}</b> · Type: {escape(analysis['detection']['type'])}</p>
    <div class='card'><div class='score'>{score['score']} / 100</div><h2>{escape(score['status'])}</h2></div>
    <div class='card'><h2>Checks</h2><table><tr><th>Check</th><th>Status</th><th>Weight</th></tr>{rows}</table></div>
    <div class='card'><h2>RunProof Doctor</h2>{issue_html}</div>
    <div class='card'><h2>Reproducibility Proof</h2><pre>{escape(json.dumps(ver,indent=2)[:10000])}</pre></div>
    <div class='card'><h2>Passport Signature</h2><code>{escape(passport['signature']['value'])}</code></div>
    </main></body></html>"""
