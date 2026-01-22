import streamlit as st
import os
import json
import hashlib
import zipfile
import io
from datetime import datetime
from source import *

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="QuLab: Lab 13: Sector Playbook Builder (Healthcare & Finance)", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Lab 13: Sector Playbook Builder (Healthcare & Finance)")
st.divider()

# --- Session State Initialization ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Sector & Use-Case Wizard"
if 'persona' not in st.session_state:
    st.session_state.persona = "AI Risk Lead (Evelyn Reed)"
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'all_use_cases' not in st.session_state:
    st.session_state.all_use_cases = []
if 'selected_use_case_display' not in st.session_state:
    st.session_state.selected_use_case_display = None
if 'selected_use_case' not in st.session_state:
    st.session_state.selected_use_case = None
if 'current_sector' not in st.session_state:
    st.session_state.current_sector = None
if 'current_system_type' not in st.session_state:
    st.session_state.current_system_type = None
if 'current_risk_tier' not in st.session_state:
    st.session_state.current_risk_tier = None
if 'current_sector_templates' not in st.session_state:
    st.session_state.current_sector_templates = None
if 'playbook_components_generated' not in st.session_state:
    st.session_state.playbook_components_generated = False
if 'ai_playbook' not in st.session_state:
    st.session_state.ai_playbook = None
if 'validation_checklist_content' not in st.session_state:
    st.session_state.validation_checklist_content = None
if 'monitoring_kpis' not in st.session_state:
    st.session_state.monitoring_kpis = None
if 'incident_triggers' not in st.session_state:
    st.session_state.incident_triggers = None
if 'final_artifacts_generated' not in st.session_state:
    st.session_state.final_artifacts_generated = False
if 'config_snapshot' not in st.session_state:
    st.session_state.config_snapshot = None
if 'executive_summary_content' not in st.session_state:
    st.session_state.executive_summary_content = None
if 'evidence_manifest' not in st.session_state:
    st.session_state.evidence_manifest = None
if 'output_dir_path' not in st.session_state:
    st.session_state.output_dir_path = None
if 'output_zip_buffer' not in st.session_state:
    st.session_state.output_zip_buffer = None
if 'output_zip_filename' not in st.session_state:
    st.session_state.output_zip_filename = None

# --- Callbacks ---

def load_data_callback():
    st.session_state.all_use_cases = load_sample_use_cases()
    st.session_state.data_loaded = True
    if st.session_state.all_use_cases:
        st.session_state.selected_use_case_display = f"{st.session_state.all_use_cases[0]['name']} ({st.session_state.all_use_cases[0]['id']})"
        update_selected_use_case()
    st.success("AI Control Templates and Use Cases Loaded!")

def update_selected_use_case():
    if st.session_state.selected_use_case_display and st.session_state.data_loaded:
        use_case_options = {f"{uc['name']} ({uc['id']})": uc['id'] for uc in st.session_state.all_use_cases}
        selected_id = use_case_options[st.session_state.selected_use_case_display]
        st.session_state.selected_use_case = select_use_case(selected_id, st.session_state.all_use_cases)
        st.session_state.current_sector = st.session_state.selected_use_case['sector']
        st.session_state.current_system_type = st.session_state.selected_use_case['system_type']
        st.session_state.current_risk_tier = st.session_state.selected_use_case['risk_tier']
        st.session_state.current_sector_templates = load_control_templates(st.session_state.current_sector)
        
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

def generate_playbook_components_callback():
    if st.session_state.selected_use_case and st.session_state.current_sector_templates:
        st.session_state.ai_playbook = generate_sector_playbook(
            st.session_state.current_sector,
            st.session_state.current_system_type,
            st.session_state.current_risk_tier,
            st.session_state.current_sector_templates
        )
        st.session_state.validation_checklist_content = generate_validation_checklist(
            st.session_state.current_sector,
            st.session_state.current_system_type,
            st.session_state.current_risk_tier,
            st.session_state.current_sector_templates
        )
        st.session_state.monitoring_kpis = generate_monitoring_kpis(
            st.session_state.current_sector,
            st.session_state.current_system_type,
            st.session_state.current_risk_tier,
            st.session_state.current_sector_templates
        )
        st.session_state.incident_triggers = generate_incident_triggers(
            st.session_state.current_sector,
            st.session_state.current_system_type,
            st.session_state.current_risk_tier,
            st.session_state.current_sector_templates
        )
        st.session_state.playbook_components_generated = True
        st.success("Playbook components generated!")
    else:
        st.error("Please load data and select a use case first.")

def generate_final_artifacts_callback():
    if st.session_state.playbook_components_generated:
        run_id = datetime.now().strftime("Session_13_%Y%m%d_%H%M%S")
        output_base_dir = "reports/session13"
        st.session_state.output_dir_path = os.path.join(output_base_dir, run_id)
        os.makedirs(st.session_state.output_dir_path, exist_ok=True)

        playbook_filename = os.path.join(st.session_state.output_dir_path, "sector_playbook.json")
        with open(playbook_filename, "w") as f:
            json.dump(st.session_state.ai_playbook, f, indent=2)

        validation_filename = os.path.join(st.session_state.output_dir_path, "validation_checklist.md")
        with open(validation_filename, "w") as f:
            f.write(st.session_state.validation_checklist_content)

        kpis_filename = os.path.join(st.session_state.output_dir_path, "monitoring_kpis.json")
        with open(kpis_filename, "w") as f:
            json.dump(st.session_state.monitoring_kpis, f, indent=2)

        triggers_filename = os.path.join(st.session_state.output_dir_path, "incident_triggers.json")
        with open(triggers_filename, "w") as f:
            json.dump(st.session_state.incident_triggers, f, indent=2)

        st.session_state.config_snapshot = create_config_snapshot(
            st.session_state.selected_use_case,
            st.session_state.ai_playbook,
            st.session_state.validation_checklist_content,
            st.session_state.monitoring_kpis,
            st.session_state.incident_triggers
        )
        snapshot_filename = os.path.join(st.session_state.output_dir_path, "config_snapshot.json")
        with open(snapshot_filename, "w") as f:
            json.dump(st.session_state.config_snapshot, f, indent=2)

        st.session_state.executive_summary_content = create_executive_summary(
            st.session_state.selected_use_case,
            st.session_state.config_snapshot
        )
        summary_filename = os.path.join(st.session_state.output_dir_path, "executive_summary.md")
        with open(summary_filename, "w") as f:
            f.write(st.session_state.executive_summary_content)

        st.session_state.evidence_manifest = generate_evidence_manifest(st.session_state.output_dir_path)

        st.session_state.output_zip_buffer = io.BytesIO()
        st.session_state.output_zip_filename = f"{run_id}.zip"
        with zipfile.ZipFile(st.session_state.output_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(st.session_state.output_dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, st.session_state.output_dir_path)
                    zf.write(file_path, arcname)
        st.session_state.output_zip_buffer.seek(0)

        st.session_state.final_artifacts_generated = True
        st.success(f"All artifacts generated and saved to '{st.session_state.output_dir_path}'!")
    else:
        st.error("Please generate playbook components first.")

# --- Sidebar ---
st.sidebar.title("AI Risk Playbook Builder")
st.sidebar.selectbox(
    "Navigation",
    options=["Sector & Use-Case Wizard", "Control Selection Preview", "Validation Checklist Builder", "Monitoring KPI Designer", "Export Panel"],
    key="current_page"
)
st.sidebar.selectbox(
    "Select Persona",
    options=["AI Risk Lead (Evelyn Reed)", "Domain AI Lead", "Model Validator"],
    key="persona"
)

# --- Page 1: Sector & Use-Case Wizard ---
if st.session_state.current_page == "Sector & Use-Case Wizard":
    st.markdown(f"## AI System Configuration & Control Explorer: Building a Sector-Specific AI Risk Playbook")
    st.markdown(f"Dr. Evelyn Reed, as the **{st.session_state.persona.split(' ')[0]}** at Global Innovations Inc., faces the critical challenge of ensuring that AI systems deployed across the company's diverse sectors meet stringent regulatory and ethical standards. Each AI initiative presents a unique combination of sector-specific nuances, technology types (Machine Learning, Large Language Models, AI Agents), and inherent risk levels. Evelyn's primary goal is to establish a systematic, transparent, and auditable approach for defining appropriate controls, validation rigor, and monitoring requirements for any given AI application.")
    st.markdown(f"This application simulates Evelyn's workflow in developing a 'Sector Playbook' for a proposed AI initiative. She will dynamically configure AI risk requirements, observe how controls adapt, and generate comprehensive documentation to justify tailored risk mitigations. This ensures proactive governance, efficient resource allocation, and clear communication with Domain AI Leads and Model Validators.")

    st.markdown(f"### Prepare Your Tools")
    st.markdown(f"Before diving into a specific AI project, Evelyn needs to prepare her tools. This involves installing necessary libraries and loading predefined control, validation, and monitoring templates. These templates are essential for her work, as they encapsulate Global Innovations Inc.'s standardized risk management policies tailored for various combinations of sector, AI system type, and risk tier. Without these pre-configured rules, she would have to manually define every control for every new AI system, a process that is prone to human error and inconsistency across the organization.")
    st.markdown(f"The control templates are structured to explicitly map a given AI system's characteristics to a recommended set of risk mitigations. For example, a high-risk LLM in healthcare will demand different validation rigor than a low-risk ML model in finance, particularly concerning false negative rates or hallucination probabilities.")

    st.button("Load AI Control Templates & Use Cases", on_click=load_data_callback, disabled=st.session_state.data_loaded)

    if st.session_state.data_loaded:
        st.success(f"Loaded {len(st.session_state.all_use_cases)} sample AI use cases and control templates.")
        st.markdown(f"---")
        st.markdown(f"### Select AI Initiative")
        st.markdown(f"Evelyn needs to evaluate a proposed AI system. Today, she's focusing on a specific scenario. Her selection of this specific use case dictates the subsequent dynamic configuration of controls, validation, and monitoring, directly demonstrating how her role adapts governance to critical applications.")
        st.markdown(f"The key parameters defining this specific initiative are its `sector`, `system_type`, and `risk_tier`. These parameters form the input to her dynamic rules engine.")

        use_case_options = {f"{uc['name']} ({uc['id']})": uc['id'] for uc in st.session_state.all_use_cases}
        
        if st.session_state.selected_use_case_display is None and use_case_options:
            st.session_state.selected_use_case_display = list(use_case_options.keys())[0]
            update_selected_use_case()

        # Find the index of the currently selected item to set the default
        current_index = 0
        if st.session_state.selected_use_case_display in list(use_case_options.keys()):
             current_index = list(use_case_options.keys()).index(st.session_state.selected_use_case_display)

        st.selectbox(
            "Choose an AI Use Case",
            options=list(use_case_options.keys()),
            index=current_index,
            key="selected_use_case_display",
            on_change=update_selected_use_case
        )

        if st.session_state.selected_use_case:
            st.markdown(f"**Selected AI Initiative:** {st.session_state.selected_use_case['name']} (`{st.session_state.selected_use_case['id']}`)")
            st.markdown(f"**Description:** {st.session_state.selected_use_case['description']}")
            st.markdown(f"**Sector:** {st.session_state.current_sector}")
            st.markdown(f"**System Type:** {st.session_state.current_system_type}")
            st.markdown(f"**Risk Tier:** {st.session_state.current_risk_tier}")
        else:
            st.warning("Please select a use case to proceed.")
        
        st.markdown(f"---")
        st.markdown(f"Evelyn has now explicitly identified the AI system she needs to govern. By selecting this system, she has established the foundational context for tailoring the risk management playbook. This precise definition is crucial, as even a slight change in sector, system type, or risk tier would lead to a vastly different set of recommended controls, demonstrating the sensitivity and specificity required in AI risk management.")
        st.button("Generate Playbook Components", key="generate_components_button", on_click=generate_playbook_components_callback, disabled=not st.session_state.selected_use_case or st.session_state.playbook_components_generated)
        if st.session_state.playbook_components_generated:
            st.success("Playbook components are ready! Navigate to 'Control Selection Preview' to see the results.")

# --- Page 2: Control Selection Preview ---
elif st.session_state.current_page == "Control Selection Preview":
    st.markdown(f"## Sector-Specific AI Control Playbook Preview")
    if st.session_state.playbook_components_generated:
        st.markdown(f"This is where Evelyn's expertise in AI risk truly comes into play. For the selected system, she needs to identify not just general AI controls, but those specifically mandated for the sector, system type, and risk level. For instance, given the potential for patient harm (Healthcare), controls around `Clinical override protocol` and `Human-in-the-loop for critical decisions` are paramount. Furthermore, the emphasis on `Privacy-preserving data handling` is critical for HIPAA compliance.")
        st.markdown(f"This section presents the generated `sector_playbook.json`, a critical artifact that outlines the foundational risk management strategy. This is an explicit response to the enterprise question: 'Given this sector, this use case, and this AI system type—what exact controls... are required?'")
        st.json(st.session_state.ai_playbook)
        st.markdown(f"Evelyn has now a concrete `sector_playbook.json` detailing the recommended controls for the selected AI system. This output directly reflects the unique challenges of the specific sector and risk level: it includes not only general data governance but also highly specific controls. This tailored approach ensures that the organization is addressing the most pertinent risks for this specific AI application, enabling the Domain AI Lead to understand exactly what governance measures are expected.")
    else:
        st.warning("Please go to 'Sector & Use-Case Wizard' and generate playbook components first.")

# --- Page 3: Validation Checklist Builder ---
elif st.session_state.current_page == "Validation Checklist Builder":
    st.markdown(f"## Validation Checklist with Specific Requirements and Thresholds")
    if st.session_state.playbook_components_generated:
        st.markdown(f"For a high-risk AI model, general validation metrics are insufficient. Evelyn needs to ensure that validation explicitly targets domain-specific safety concerns, particularly mitigating false negatives (in Healthcare) or ensuring fairness (in Finance). The validation requirements must be rigorous, and the acceptance thresholds for metrics like `False Negative Rate (FNR)` must be extremely strict.")
        st.markdown(r"For instance, for a high-risk Healthcare ML model, the requirement for critical diagnoses is $FNR_{\text{target\_condition}} < 0.01$.")
        st.markdown(r"where $FNR_{\text{target\_condition}}$ is the False Negative Rate for patients with critical conditions.")
        st.markdown(r"She also requires evaluation of `Bias fairness metrics`, for example, to ensure that the difference in FNR between protected groups and the overall population ($|FNR_{\text{protected\_group}} - FNR_{\text{overall}}| < 0.02$) remains within acceptable clinical bounds.")
        st.markdown(r"where $FNR_{\text{protected\_group}}$ is the False Negative Rate for a specific protected demographic group, and $FNR_{\text{overall}}$ is the overall False Negative Rate.")
        st.markdown(f"This directly supports the learning objective of translating technical risk into domain-relevant control expectations and specifying validation depth.")
        st.markdown(f"---")
        st.markdown(st.session_state.validation_checklist_content)
        st.markdown(f"---")
        st.markdown(f"The generated `validation_checklist.md` provides a precise set of criteria for model validators. For the selected system, Evelyn has specified not only general performance metrics but also critical thresholds for `False Negative Rate` and `Bias in FNR across protected groups`. These quantitative measures provide objective benchmarks that model validators must meet before the system can be considered safe for deployment, directly tying technical evaluation to real-world patient safety.")
    else:
        st.warning("Please go to 'Sector & Use-Case Wizard' and generate playbook components first.")

# --- Page 4: Monitoring KPI Designer ---
elif st.session_state.current_page == "Monitoring KPI Designer":
    st.markdown(f"## Monitoring KPIs and Incident Triggers")
    if st.session_state.playbook_components_generated:
        st.markdown(f"After deployment, the AI system must be continuously monitored for safety and performance. Evelyn needs to define specific `Monitoring KPIs` and `Incident Triggers` that reflect the high-stakes nature of the system and sector.")
        st.markdown(f"For example, `Outcome drift` and `Override rates` are crucial to detect if the model's recommendations are changing or being frequently rejected by human operators, potentially indicating a degradation in performance or an emerging bias. An `Alert fatigue` metric is also included to ensure that human operators are not overwhelmed by non-critical alerts, which could lead to missed critical incidents (e.g., in Healthcare).")
        st.markdown(f"These definitions translate directly into operational readiness, providing clear signals for when human intervention or model retraining is required, thereby ensuring ongoing risk mitigation.")
        st.markdown(f"---")
        st.subheader("Monitoring KPIs")
        st.json(st.session_state.monitoring_kpis)
        st.subheader("Incident Triggers")
        st.json(st.session_state.incident_triggers)
        st.markdown(f"---")
        st.markdown(f"Evelyn has successfully defined the critical `monitoring_kpis.json` and `incident_triggers.json` for the selected AI system. The generated KPIs provide a clear dashboard for observing the model's ongoing health and safety. The incident triggers define concrete thresholds for when an alert must be raised and human intervention initiated. This proactive monitoring framework is crucial for maintaining patient safety and regulatory compliance post-deployment.")
    else:
        st.warning("Please go to 'Sector & Use-Case Wizard' and generate playbook components first.")

# --- Page 5: Export Panel ---
elif st.session_state.current_page == "Export Panel":
    st.markdown(f"## Generate & Export AI Risk Playbook Artifacts")
    if st.session_state.playbook_components_generated:
        st.markdown(f"As AI Risk Lead, Evelyn needs to present a concise yet comprehensive summary of the AI system's governance posture to senior leadership and cross-functional teams. This involves consolidating the derived controls, validation, and monitoring into a `config_snapshot.json` and generating an `executive_summary.md`.")
        st.markdown(f"The executive summary is particularly important for justifying *why* certain controls are in place, explicitly connecting them back to the risks inherent in the AI system. This artifact supports strategic planning and resource allocation by providing a clear rationale for the chosen risk mitigations.")
        
        st.button("Generate All Final Artifacts", key="generate_final_artifacts_button", on_click=generate_final_artifacts_callback, disabled=st.session_state.final_artifacts_generated)

        if st.session_state.final_artifacts_generated:
            st.success("All final artifacts generated successfully!")
            st.markdown(f"### Evidence Manifest for Auditability")
            st.markdown(f"In regulated industries like Healthcare and Finance, auditability is paramount. Evelyn must ensure that all generated risk management artifacts are immutable and verifiable. By computing SHA-256 hashes for each file and recording them in an `evidence_manifest.json`, she creates a robust audit trail.")
            st.markdown(r"The SHA-256 hash, $H(M)$, for a message (file content) $M$, is a cryptographic hash function that produces a 256-bit (32-byte) hash value, a nearly unique \"digital fingerprint\" of the input. Any tiny change to the input file will result in a completely different hash value, making it ideal for verifying file integrity:")
            st.markdown(r"$$H_{\text{SHA-256}}(M) = \text{hash value}$$")
            st.markdown(r"where $M$ represents the content of the file, and $\text{hash value}$ is the unique 256-bit hexadecimal string.")
            st.markdown(f"This manifest serves as proof that the playbooks, checklists, and summaries generated reflect the exact state of the risk assessment at a given point in time. This mechanism is crucial for demonstrating compliance to internal and external auditors, aligning with the overall goal of enterprise AI governance.")
            st.markdown(f"---")
            st.subheader("Generated Configuration Snapshot (`config_snapshot.json`)")
            st.json(st.session_state.config_snapshot)
            st.subheader("Generated Executive Summary (`executive_summary.md`)")
            st.markdown(st.session_state.executive_summary_content)
            st.subheader("Generated Evidence Manifest (`evidence_manifest.json`)")
            st.json(st.session_state.evidence_manifest)
            
            st.markdown(f"---")
            st.markdown(f"**Output Directory:** `{st.session_state.output_dir_path}`")
            if st.session_state.output_zip_buffer and st.session_state.output_zip_filename:
                st.download_button(
                    label="Download All Artifacts as ZIP",
                    data=st.session_state.output_zip_buffer.getvalue(),
                    file_name=st.session_state.output_zip_filename,
                    mime="application/zip"
                )
            
            st.markdown(f"---")
            st.markdown(f"### Workflow Complete")
            st.markdown(f"Dr. Evelyn Reed has successfully generated a comprehensive AI Risk Playbook for the '{st.session_state.selected_use_case['name']}' initiative, tailored for the {st.session_state.selected_use_case['sector']} sector and its {st.session_state.selected_use_case['risk_tier']} risk tier.")
            st.markdown(f"All artifacts, including a detailed executive summary and an audit evidence manifest, have been created. This ensures proactive governance and provides a clear path for Model Validators and Domain AI Leads to manage the AI system effectively.")
        else:
            st.info("Click 'Generate All Final Artifacts' to create the exportable documents.")
    else:
        st.warning("Please go to 'Sector & Use-Case Wizard' and generate playbook components first.")


# License
st.caption('''
---
## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
