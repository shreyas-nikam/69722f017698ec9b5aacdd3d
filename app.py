import pandas as pd
import streamlit as st
import os
import json
import zipfile
import io
from datetime import datetime

# Import only the functions you need (avoid star imports)
from source import (
    load_sample_use_cases,
    load_control_templates,
    select_use_case,
    generate_sector_playbook,
    generate_validation_checklist,
    generate_monitoring_kpis,
    generate_incident_triggers,
    create_config_snapshot,
    create_executive_summary,
    generate_evidence_manifest,
    generate_all_artifacts,
)

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="QuLab: Lab 13: Sector Playbook Builder (Healthcare & Finance)",
    layout="wide",
)
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Lab 13: Sector Playbook Builder (Healthcare & Finance)")
st.divider()

# --- Session State Initialization ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Sector & Use-Case Wizard"
if "persona" not in st.session_state:
    st.session_state.persona = "AI Risk Lead (Evelyn Reed)"
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "all_use_cases" not in st.session_state:
    st.session_state.all_use_cases = []
if "selected_use_case_display" not in st.session_state:
    st.session_state.selected_use_case_display = None
if "selected_use_case" not in st.session_state:
    st.session_state.selected_use_case = None
if "current_sector" not in st.session_state:
    st.session_state.current_sector = None
if "current_system_type" not in st.session_state:
    st.session_state.current_system_type = None
if "current_risk_tier" not in st.session_state:
    st.session_state.current_risk_tier = None
if "current_sector_templates" not in st.session_state:
    st.session_state.current_sector_templates = None
if "playbook_components_generated" not in st.session_state:
    st.session_state.playbook_components_generated = False
if "ai_playbook" not in st.session_state:
    st.session_state.ai_playbook = None
if "validation_checklist_content" not in st.session_state:
    st.session_state.validation_checklist_content = None
if "monitoring_kpis" not in st.session_state:
    st.session_state.monitoring_kpis = None
if "incident_triggers" not in st.session_state:
    st.session_state.incident_triggers = None
if "final_artifacts_generated" not in st.session_state:
    st.session_state.final_artifacts_generated = False
if "config_snapshot" not in st.session_state:
    st.session_state.config_snapshot = None
if "executive_summary_content" not in st.session_state:
    st.session_state.executive_summary_content = None
if "evidence_manifest" not in st.session_state:
    st.session_state.evidence_manifest = None
if "output_dir_path" not in st.session_state:
    st.session_state.output_dir_path = None
if "output_zip_buffer" not in st.session_state:
    st.session_state.output_zip_buffer = None
if "output_zip_filename" not in st.session_state:
    st.session_state.output_zip_filename = None


# --- Callbacks ---


def _chips(items, chip_height_px: int = 34):
    """Render list of items as 'pill' chips using Streamlit markdown + inline CSS."""
    if not items:
        st.info("No items available.")
        return
    css = f"""
    <style>
      .chip-wrap {{ display:flex; flex-wrap:wrap; gap:8px; }}
      .chip {{
        display:inline-flex; align-items:center; padding:0 12px; height:{chip_height_px}px;
        border-radius:999px; border:1px solid rgba(49,51,63,0.2);
        background: rgba(49,51,63,0.04); font-size:0.95rem;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    html = '<div class="chip-wrap">' + \
        "".join(
            [f'<div class="chip">{str(x)}</div>' for x in items]) + "</div>"
    # Fallback if Streamlit internals change: don't rely on _escape_markdown
    html = '<div class="chip-wrap">' + \
        "".join(
            [f'<div class="chip">{str(x)}</div>' for x in items]) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_use_case_dashboard(use_case: dict):
    st.subheader("Use Case Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sector", use_case.get("sector", "—"))
    c2.metric("System Type", use_case.get("system_type", "—"))
    c3.metric("Risk Tier", use_case.get("risk_tier", "—"))
    c4.metric("Use Case ID", use_case.get("id", "—"))

    st.markdown(f"### {use_case.get('name', '(Unnamed)')}")
    st.markdown(use_case.get("description", ""))


def render_playbook_dashboard(playbook: dict):
    st.subheader("Sector Playbook")
    top = st.container()
    with top:
        c1, c2, c3 = st.columns(3)
        c1.metric("Sector", playbook.get("sector", "—"))
        c2.metric("System Type", playbook.get("system_type", "—"))
        c3.metric("Risk Tier", playbook.get("risk_tier", "—"))

        st.markdown("**Sector Emphasis**")
        st.info(playbook.get("sector_emphasis", "—"))

    st.markdown("**Controls**")
    _chips(playbook.get("controls", []))
    st.markdown("")


def render_validation_dashboard(validation_md: str):
    st.subheader("Validation Checklist")
    # Pull checklist items (lines starting with "- [ ]")
    items = []
    for ln in (validation_md or "").splitlines():
        ln = ln.strip()
        if ln.startswith("- [ ] "):
            items.append({"Validation Item": ln.replace("- [ ] ", "").strip()})

    if items:
        st.markdown("**Checklist Items**")
        df = pd.DataFrame(items)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} validation activities")
    else:
        st.warning("No checklist items found.")

    with st.expander("Full Markdown (validation_checklist.md)"):
        st.markdown(validation_md or "")


def render_monitoring_dashboard(kpis: list, triggers: list):
    st.subheader("Monitoring & Incident Response")

    c1, c2 = st.columns(2)
    c1.metric("Monitoring KPIs", len(kpis or []))
    c2.metric("Incident Triggers", len(triggers or []))

    left, right = st.columns(2)

    with left:
        st.markdown("### Monitoring KPIs")
        if kpis:
            st.dataframe(pd.DataFrame({"KPI": kpis}),
                         use_container_width=True, hide_index=True)
        else:
            st.info("No KPIs available.")

    with right:
        st.markdown("### Incident Triggers")
        if triggers:
            st.dataframe(pd.DataFrame({"Trigger": triggers}),
                         use_container_width=True, hide_index=True)
        else:
            st.info("No incident triggers available.")


def render_snapshot_dashboard(snapshot: dict):
    st.subheader("Configuration Snapshot")
    use_case = snapshot.get("use_case_details", {}) if snapshot else {}
    playbook = snapshot.get("ai_playbook", {}) if snapshot else {}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sector", use_case.get("sector", "—"))
    c2.metric("Type", use_case.get("system_type", "—"))
    c3.metric("Risk", use_case.get("risk_tier", "—"))
    c4.metric("Generated", (snapshot.get(
        "generated_timestamp", "—")[:19] if snapshot else "—"))

    st.markdown("**Controls (from playbook)**")
    _chips(playbook.get("controls", []))

    st.markdown("**Acceptance Thresholds**")
    thresholds = snapshot.get("acceptance_thresholds", []) if snapshot else []
    if thresholds:
        st.dataframe(pd.DataFrame({"Threshold": thresholds}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No thresholds configured for this combination.")

    st.markdown("**Validation Requirements**")
    reqs = snapshot.get("validation_requirements", []) if snapshot else []
    if reqs:
        st.dataframe(pd.DataFrame({"Requirement": reqs}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No validation requirements available.")

    monitoring_kpis = snapshot.get("monitoring_kpis", []) if snapshot else []
    incident_triggers = snapshot.get(
        "incident_triggers", []) if snapshot else []

    if monitoring_kpis or incident_triggers:
        st.markdown("**Monitoring & Incident Response**")
        mkpis = pd.DataFrame({"KPI": monitoring_kpis}
                             ) if monitoring_kpis else pd.DataFrame()
        itriggers = pd.DataFrame(
            {"Trigger": incident_triggers}) if incident_triggers else pd.DataFrame()

        left, right = st.columns(2)

        with left:
            st.markdown("#### Monitoring KPIs")
            if not mkpis.empty:
                st.dataframe(mkpis, use_container_width=True, hide_index=True)
            else:
                st.info("No KPIs available.")

        with right:
            st.markdown("#### Incident Triggers")
            if not itriggers.empty:
                st.dataframe(itriggers, use_container_width=True,
                             hide_index=True)
            else:
                st.info("No incident triggers available.")


def render_evidence_manifest_dashboard(manifest: dict):
    st.subheader("Evidence Manifest (Auditability)")
    artifacts = (manifest or {}).get("artifacts", [])
    ts = (manifest or {}).get("manifest_timestamp", "—")

    c1, c2 = st.columns(2)
    c1.metric("Artifacts Tracked", len(artifacts))
    c2.metric("Manifest Timestamp", ts[:19] if isinstance(ts, str) else "—")

    if artifacts:
        rows = []
        missing = 0
        for a in artifacts:
            status = "OK" if "sha256_hash" in a else a.get("status", "UNKNOWN")
            if status != "OK":
                missing += 1
            rows.append(
                {
                    "Filename": a.get("filename", ""),
                    "Status": status,
                    "SHA-256 (prefix)": (a.get("sha256_hash", "")[:16] + "…") if a.get("sha256_hash") else "",
                    "Path": a.get("filepath", ""),
                }
            )
        st.dataframe(pd.DataFrame(rows),
                     use_container_width=True, hide_index=True)
        if missing:
            st.warning(f"{missing} artifact(s) missing.")
    else:
        st.info("No artifacts recorded in manifest.")


def _reset_generated_state():
    st.session_state.playbook_components_generated = False
    st.session_state.final_artifacts_generated = False
    st.session_state.ai_playbook = None
    st.session_state.validation_checklist_content = None
    st.session_state.monitoring_kpis = None
    st.session_state.incident_triggers = None
    st.session_state.config_snapshot = None
    st.session_state.executive_summary_content = None
    st.session_state.evidence_manifest = None
    st.session_state.output_dir_path = None
    st.session_state.output_zip_buffer = None
    st.session_state.output_zip_filename = None


def load_data_callback():
    # source.py ensures data files exist; just load
    st.session_state.all_use_cases = load_sample_use_cases(data_dir="data")
    st.session_state.data_loaded = True

    if st.session_state.all_use_cases:
        first = st.session_state.all_use_cases[0]
        st.session_state.selected_use_case_display = f"{first['name']} ({first['id']})"
        update_selected_use_case()

    st.success("AI Control Templates and Use Cases Loaded!")


def update_selected_use_case():
    if st.session_state.selected_use_case_display and st.session_state.data_loaded:
        use_case_options = {
            f"{uc['name']} ({uc['id']})": uc["id"] for uc in st.session_state.all_use_cases}
        selected_id = use_case_options[st.session_state.selected_use_case_display]

        st.session_state.selected_use_case = select_use_case(
            selected_id, st.session_state.all_use_cases)

        if not st.session_state.selected_use_case:
            st.error(f"Use case with ID {selected_id} not found.")
            _reset_generated_state()
            return

        st.session_state.current_sector = st.session_state.selected_use_case["sector"]
        st.session_state.current_system_type = st.session_state.selected_use_case[
            "system_type"]
        st.session_state.current_risk_tier = st.session_state.selected_use_case["risk_tier"]

        # Load templates for sector
        st.session_state.current_sector_templates = load_control_templates(
            st.session_state.current_sector,
            data_dir="data",
        )

        _reset_generated_state()


def generate_playbook_components_callback():
    use_case = st.session_state.selected_use_case
    templates = st.session_state.current_sector_templates

    if use_case and templates:
        st.session_state.ai_playbook = generate_sector_playbook(
            sector=use_case["sector"],
            system_type=use_case["system_type"],
            risk_tier=use_case["risk_tier"],
            templates=templates,
        )

        # NEW signature: generate_validation_checklist(use_case, templates)
        st.session_state.validation_checklist_content = generate_validation_checklist(
            use_case=use_case,
            templates=templates,
        )

        # NEW signature: generate_monitoring_kpis(use_case, templates)
        st.session_state.monitoring_kpis = generate_monitoring_kpis(
            use_case=use_case,
            templates=templates,
        )

        # NEW signature: generate_incident_triggers(use_case, templates)
        st.session_state.incident_triggers = generate_incident_triggers(
            use_case=use_case,
            templates=templates,
        )

        st.session_state.playbook_components_generated = True
        st.success("Playbook components generated!")
    else:
        st.error("Please load data and select a use case first.")


def generate_final_artifacts_callback():
    """
    Use the orchestration API in source.py so the export behavior stays consistent.
    We still keep in-memory state for rendering in Streamlit.
    """
    if not st.session_state.playbook_components_generated:
        st.error("Please generate playbook components first.")
        return

    run_id = datetime.now().strftime("Session_13_%Y%m%d_%H%M%S")
    output_base_dir = "reports/session13"
    output_dir = os.path.join(output_base_dir, run_id)
    os.makedirs(output_dir, exist_ok=True)

    # Determine AI Risk Lead name from persona (optional polish)
    ai_risk_lead = "Dr. Evelyn Reed" if "Evelyn" in st.session_state.persona else st.session_state.persona

    # Use source.py orchestrator to (1) write files, (2) compute manifest, (3) return in-memory objects
    result = generate_all_artifacts(
        use_case_id=st.session_state.selected_use_case["id"],
        data_dir="data",
        output_dir=output_dir,
        ai_risk_lead=ai_risk_lead,
        write_files=True,
    )

    # Populate Streamlit session state from result (for display)
    st.session_state.output_dir_path = output_dir
    st.session_state.ai_playbook = result.playbook
    st.session_state.validation_checklist_content = result.validation_checklist_md
    st.session_state.monitoring_kpis = result.monitoring_kpis
    st.session_state.incident_triggers = result.incident_triggers
    st.session_state.config_snapshot = result.config_snapshot
    st.session_state.executive_summary_content = result.executive_summary_md
    st.session_state.evidence_manifest = result.evidence_manifest

    # Zip output directory
    st.session_state.output_zip_buffer = io.BytesIO()
    st.session_state.output_zip_filename = f"{run_id}.zip"

    with zipfile.ZipFile(st.session_state.output_zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zf.write(file_path, arcname)

    st.session_state.output_zip_buffer.seek(0)

    st.session_state.final_artifacts_generated = True
    st.success(f"All artifacts generated and saved to '{output_dir}'!")


# --- Sidebar ---
st.sidebar.title("AI Risk Playbook Builder")
st.sidebar.selectbox(
    "Navigation",
    options=[
        "Sector & Use-Case Wizard",
        "Control Selection Preview",
        "Validation Checklist Builder",
        "Monitoring KPI Designer",
        "Export Panel",
    ],
    key="current_page",
)
st.session_state.persona = "AI Risk Lead (Evelyn Reed)"

# --- Page 1: Sector & Use-Case Wizard ---
if st.session_state.current_page == "Sector & Use-Case Wizard":
    st.markdown(
        "## AI System Configuration & Control Explorer: Building a Sector-Specific AI Risk Playbook")
    st.markdown(
        f"Dr. Evelyn Reed, as the **{st.session_state.persona.split(' ')[0]}** at Global Innovations Inc., faces the "
        "critical challenge of ensuring that AI systems deployed across the company's diverse sectors meet stringent "
        "regulatory and ethical standards. Each AI initiative presents a unique combination of sector-specific nuances, "
        "technology types (Machine Learning, Large Language Models, AI Agents), and inherent risk levels."
    )
    st.markdown(
        "This application simulates Evelyn's workflow in developing a 'Sector Playbook' for a proposed AI initiative. "
        "She will dynamically configure AI risk requirements, observe how controls adapt, and generate comprehensive "
        "documentation to justify tailored risk mitigations."
    )

    st.markdown("### Prepare Your Tools")
    st.button(
        "Load AI Control Templates & Use Cases",
        on_click=load_data_callback,
        disabled=st.session_state.data_loaded,
    )

    if st.session_state.data_loaded:
        st.success(
            f"Loaded {len(st.session_state.all_use_cases)} sample AI use cases and control templates.")
        st.markdown("---")
        st.markdown("### Select AI Initiative")

        use_case_options = {
            f"{uc['name']} ({uc['id']})": uc["id"] for uc in st.session_state.all_use_cases}

        if st.session_state.selected_use_case_display is None and use_case_options:
            st.session_state.selected_use_case_display = list(
                use_case_options.keys())[0]
            update_selected_use_case()

        current_index = 0
        if st.session_state.selected_use_case_display in list(use_case_options.keys()):
            current_index = list(use_case_options.keys()).index(
                st.session_state.selected_use_case_display)

        st.selectbox(
            "Choose an AI Use Case",
            options=list(use_case_options.keys()),
            index=current_index,
            key="selected_use_case_display",
            on_change=update_selected_use_case,
        )

        if st.session_state.selected_use_case:
            st.markdown(
                f"**Selected AI Initiative:** {st.session_state.selected_use_case['name']} "
                f"(`{st.session_state.selected_use_case['id']}`)"
            )
            st.markdown(
                f"**Description:** {st.session_state.selected_use_case['description']}")
            st.markdown(f"**Sector:** {st.session_state.current_sector}")
            st.markdown(
                f"**System Type:** {st.session_state.current_system_type}")
            st.markdown(f"**Risk Tier:** {st.session_state.current_risk_tier}")
        else:
            st.warning("Please select a use case to proceed.")

        st.markdown("---")
        st.button(
            "Generate Playbook Components",
            key="generate_components_button",
            on_click=generate_playbook_components_callback,
            disabled=not st.session_state.selected_use_case or st.session_state.playbook_components_generated,
        )
        if st.session_state.playbook_components_generated:
            st.success(
                "Playbook components are ready! Navigate to 'Control Selection Preview' to see the results.")


# --- Page 2: Control Selection Preview ---
elif st.session_state.current_page == "Control Selection Preview":
    st.markdown("## Sector-Specific AI Control Playbook Preview")
    if st.session_state.playbook_components_generated:
        render_playbook_dashboard(st.session_state.ai_playbook)
    else:
        st.warning(
            "Please go to 'Sector & Use-Case Wizard' and generate playbook components first.")


# --- Page 3: Validation Checklist Builder ---
elif st.session_state.current_page == "Validation Checklist Builder":
    st.markdown(
        "## Validation Checklist with Specific Requirements and Thresholds")
    if st.session_state.playbook_components_generated:
        st.markdown(st.session_state.validation_checklist_content)
    else:
        st.warning(
            "Please go to 'Sector & Use-Case Wizard' and generate playbook components first.")


# --- Page 4: Monitoring KPI Designer ---
elif st.session_state.current_page == "Monitoring KPI Designer":
    st.markdown("## Monitoring KPIs and Incident Triggers")
    if st.session_state.playbook_components_generated:
        render_monitoring_dashboard(
            st.session_state.monitoring_kpis, st.session_state.incident_triggers)
    else:
        st.warning(
            "Please go to 'Sector & Use-Case Wizard' and generate playbook components first.")


# --- Page 5: Export Panel ---
elif st.session_state.current_page == "Export Panel":
    st.markdown("## Generate & Export AI Risk Playbook Artifacts")
    if st.session_state.playbook_components_generated:
        st.button(
            "Generate All Final Artifacts",
            key="generate_final_artifacts_button",
            on_click=generate_final_artifacts_callback,
            disabled=st.session_state.final_artifacts_generated,
        )

        if st.session_state.final_artifacts_generated:
            st.success("All final artifacts generated successfully!")

            st.subheader(
                "Generated Configuration Snapshot (`config_snapshot.json`)")
            render_snapshot_dashboard(st.session_state.config_snapshot)

            st.subheader(
                "Generated Executive Summary (`executive_summary.md`)")
            with st.container(border=True):
                st.markdown(st.session_state.executive_summary_content)

            st.subheader(
                "Generated Evidence Manifest (`evidence_manifest.json`)")
            render_evidence_manifest_dashboard(
                st.session_state.evidence_manifest)

            st.markdown("---")
            st.markdown(
                f"**Output Directory:** `{st.session_state.output_dir_path}`")

            if st.session_state.output_zip_buffer and st.session_state.output_zip_filename:
                st.download_button(
                    label="Download All Artifacts as ZIP",
                    data=st.session_state.output_zip_buffer.getvalue(),
                    file_name=st.session_state.output_zip_filename,
                    mime="application/zip",
                )
        else:
            st.info(
                "Click 'Generate All Final Artifacts' to create the exportable documents.")
    else:
        st.warning(
            "Please go to 'Sector & Use-Case Wizard' and generate playbook components first.")


# License
st.caption(
    """
---
## QuantUniversity License

© QuantUniversity 2025
This notebook was created for **educational purposes only** and is **not intended for commercial use**.

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.
- You **may not delete or modify this license cell** without authorization.
- This notebook was generated using **QuCreate**, an AI-powered assistant.
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
"""
)
