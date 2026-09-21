"""Gradio UI mounted inside FastAPI."""

from io import StringIO

import pandas as pd

from app.services.anomaly_service import AnomalyService
from app.services.health_service import HealthService
from app.services.query_service import QueryService
from app.services.state import AppState

NAVY = "#1F2A44"
WARM_BEIGE = "#E8DCC8"
SOFT_GOLD = "#C6A75E"

APP_CSS = f"""
:root {{
    --navy: {NAVY};
    --warm-beige: {WARM_BEIGE};
    --soft-gold: {SOFT_GOLD};
    --ink: #182033;
    --muted: #6d675d;
    --surface: rgba(255, 252, 246, 0.92);
    --line: rgba(31, 42, 68, 0.14);
}}

.gradio-container {{
    background:
        radial-gradient(circle at top left, rgba(198, 167, 94, 0.34), transparent 34rem),
        linear-gradient(135deg, #1f2a44 0%, #263651 38%, #e8dcc8 38%, #f7efe2 100%);
    color: var(--ink);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

#app-shell {{
    max-width: 1220px;
    margin: 0 auto;
}}

#hero {{
    position: relative;
    overflow: hidden;
    padding: 34px 36px;
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 22px;
    background:
        linear-gradient(135deg, rgba(31,42,68,0.96) 0%, rgba(31,42,68,0.88) 45%, rgba(198,167,94,0.88) 100%);
    box-shadow: 0 24px 70px rgba(18, 24, 38, 0.24);
}}

#hero h1 {{
    margin: 0;
    color: #fffaf0;
    font-size: 38px;
    line-height: 1.08;
    font-weight: 800;
    letter-spacing: 0;
}}

#hero p {{
    max-width: 780px;
    margin: 12px 0 0;
    color: rgba(255, 250, 240, 0.84);
    font-size: 16px;
}}

.metric-row {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin: 18px 0 6px;
}}

.metric {{
    padding: 16px 18px;
    border-radius: 16px;
    background: rgba(255, 250, 240, 0.12);
    border: 1px solid rgba(255, 250, 240, 0.22);
}}

.metric span {{
    display: block;
    color: rgba(255, 250, 240, 0.72);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.metric strong {{
    display: block;
    margin-top: 6px;
    color: #fffaf0;
    font-size: 24px;
}}

.panel {{
    border: 1px solid var(--line) !important;
    border-radius: 18px !important;
    background: var(--surface) !important;
    box-shadow: 0 18px 48px rgba(31, 42, 68, 0.12) !important;
}}

button.primary {{
    background: linear-gradient(135deg, var(--soft-gold), #d9bf76) !important;
    color: var(--navy) !important;
    border: 0 !important;
    font-weight: 800 !important;
}}

button.secondary {{
    border-color: var(--navy) !important;
    color: #fffaf0 !important;
    background: var(--navy) !important;
    font-weight: 800 !important;
}}

.example-panel {{
    padding: 14px !important;
    border-radius: 14px !important;
    background: rgba(31, 42, 68, 0.92) !important;
    border: 1px solid rgba(255, 250, 240, 0.16) !important;
}}

.example-button {{
    background: rgba(12, 18, 31, 0.94) !important;
    color: #fffaf0 !important;
    border: 1px solid rgba(198, 167, 94, 0.55) !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 22px rgba(12, 18, 31, 0.22) !important;
    text-align: left !important;
    justify-content: flex-start !important;
}}

.example-button:hover {{
    background: var(--soft-gold) !important;
    color: var(--navy) !important;
    border-color: var(--soft-gold) !important;
}}

.tabs button {{
    font-weight: 700 !important;
}}

label, .label-wrap span {{
    color: var(--navy) !important;
    font-weight: 700 !important;
}}

textarea, input, select {{
    border-color: rgba(31, 42, 68, 0.18) !important;
}}

@media (max-width: 860px) {{
    #hero {{
        padding: 26px 22px;
        border-radius: 16px;
    }}
    #hero h1 {{
        font-size: 30px;
    }}
    .metric-row {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
}}
"""


def create_ui(state: AppState):
    """Create the Gradio Blocks UI."""

    import gradio as gr

    query_service = QueryService(state)
    anomaly_service = AnomalyService(state)
    health_service = HealthService(state)

    def ask(question: str):
        try:
            result = query_service.ask(question)
            return (
                result["answer"],
                pd.DataFrame(result["rows"]),
                "\n".join(result["assumptions"] + result["warnings"]),
            )
        except Exception as exc:  # UI should display service errors plainly.
            return str(exc), pd.DataFrame(), ""

    def list_anomalies(rule: str, priority: str, limit: int):
        rule_value = None if rule == "all" else rule
        priority_value = None if priority == "all" else priority
        result = anomaly_service.list_anomalies(rule=rule_value, priority=priority_value, limit=int(limit))
        frame = pd.DataFrame(result["rows"])
        buffer = StringIO()
        frame.to_csv(buffer, index=False)
        return frame, result["counts_by_rule"], buffer.getvalue()

    def health():
        return health_service.get_health()

    example_questions = [
        "How many tickets are currently open?",
        "Which agent resolved the most tickets this month?",
        "Show me all Critical tickets not resolved within 12 hours.",
        "What is the average customer rating for Technical category tickets?",
        "Are there any anomalies in resolution times this week?",
    ]

    health_snapshot = health_service.get_health()
    quality = health_snapshot["data_quality"]
    hero = f"""
<div id="app-shell">
  <section id="hero">
    <h1>Support Ticket Intelligence</h1>
    <p>Ask operational questions, inspect anomaly signals, and verify data health from the provided 500-ticket support dataset.</p>
    <div class="metric-row">
      <div class="metric"><span>Tickets</span><strong>{health_snapshot["rows"]}</strong></div>
      <div class="metric"><span>Open</span><strong>{quality["status_counts"].get("Open", 0)}</strong></div>
      <div class="metric"><span>Escalated</span><strong>{quality["status_counts"].get("Escalated", 0)}</strong></div>
      <div class="metric"><span>As of</span><strong>{str(health_snapshot["as_of"])[:10]}</strong></div>
    </div>
  </section>
</div>
"""

    with gr.Blocks(title="Support Ticket Intelligence", css=APP_CSS, theme=gr.themes.Soft()) as demo:
        gr.HTML(hero)
        with gr.Tab("Ask"):
            with gr.Row():
                with gr.Column(scale=5, elem_classes=["panel"]):
                    question = gr.Textbox(
                        label="Ask a ticket question",
                        value="How many tickets are currently open?",
                        lines=3,
                        placeholder="Try: Which agent resolved the most tickets this month?",
                    )
                    with gr.Row():
                        submit = gr.Button("Ask", variant="primary", elem_classes=["primary"])
                        clear = gr.ClearButton([question], value="Clear", elem_classes=["secondary"])
                    gr.Markdown("Examples")
                    with gr.Column(elem_classes=["example-panel"]):
                        for example in example_questions:
                            example_button = gr.Button(example, elem_classes=["example-button"])
                            example_button.click(lambda value=example: value, outputs=question)
                with gr.Column(scale=4, elem_classes=["panel"]):
                    answer = gr.Textbox(label="Answer", lines=5, show_copy_button=True)
                    details = gr.Textbox(label="Assumptions and warnings", lines=5)
            rows = gr.Dataframe(label="Result rows", elem_classes=["panel"], wrap=True)
            submit.click(ask, inputs=question, outputs=[answer, rows, details])

        with gr.Tab("Anomalies"):
            with gr.Row():
                with gr.Column(scale=3, elem_classes=["panel"]):
                    rule = gr.Dropdown(
                        ["all", "resolution_outlier", "stale_unresolved", "response_sla", "data_integrity"],
                        value="all",
                        label="Rule",
                    )
                    priority = gr.Radio(["all", "Low", "Medium", "High", "Critical"], value="all", label="Priority")
                    limit = gr.Slider(10, 500, value=100, step=10, label="Limit")
                    run = gr.Button("Find anomalies", variant="primary", elem_classes=["primary"])
                with gr.Column(scale=2, elem_classes=["panel"]):
                    counts = gr.JSON(label="Counts by rule")
            anomaly_rows = gr.Dataframe(label="Anomaly flags", elem_classes=["panel"], wrap=True)
            csv_text = gr.Textbox(label="CSV export", lines=5, show_copy_button=True)
            run.click(list_anomalies, inputs=[rule, priority, limit], outputs=[anomaly_rows, counts, csv_text])

        with gr.Tab("Data & Health"):
            with gr.Row():
                refresh = gr.Button("Refresh health", variant="primary", elem_classes=["primary"])
            health_json = gr.JSON(label="Health and data quality", elem_classes=["panel"])
            refresh.click(health, outputs=health_json)
            demo.load(health, outputs=health_json)

    return demo
