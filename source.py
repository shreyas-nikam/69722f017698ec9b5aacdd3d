# source.py
from __future__ import annotations

import json
import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# Defaults (synthetic templates)
# -----------------------------

def get_default_healthcare_control_templates() -> Dict[str, Any]:
    return {
        "ML": {
            "Low": {
                "controls": ["Data governance (Healthcare)", "Model documentation (Healthcare)"],
                "validation": [
                    "Basic performance metrics (accuracy, $P(\\text{correct}) > 0.8$)",
                    "Data quality check ($missing\\_data < 5\\%$)",
                ],
                "monitoring": ["Model drift (basic)", "Prediction integrity"],
                "incident_triggers": ["Significant performance drop (e.g., accuracy below $0.75$)"],
            },
            "Medium": {
                "controls": [
                    "Data governance (Healthcare)",
                    "Model documentation (Healthcare)",
                    "Bias detection (demographics)",
                    "Robustness testing (Healthcare specific)",
                ],
                "validation": [
                    "Advanced performance (AUC, F1, Sensitivity, Specificity)",
                    "Bias fairness metrics (e.g., $FNR_{groupA} - FNR_{groupB} < 0.05$)",
                    "Outlier detection",
                ],
                "monitoring": [
                    "Model drift (detailed)",
                    "Fairness metric drift",
                    "Outcome drift (e.g., re-hospitalization rates)",
                ],
                "incident_triggers": [
                    "Unacceptable bias detected",
                    "Unexplained outcome changes",
                    "High override rate ($>10\\%$ of predictions)",
                ],
            },
            "High": {
                "controls": [
                    "Data governance (Healthcare)",
                    "Model documentation (Healthcare)",
                    "Bias detection (demographics)",
                    "Robustness testing (Healthcare specific)",
                    "Clinical override protocol",
                    "Human-in-the-loop for critical decisions",
                    "Explainability for clinicians",
                    "Privacy-preserving data handling (HIPAA compliance)",
                ],
                "validation": [
                    "Comprehensive performance (Sensitivity, Specificity, $FNR_{target\\_condition} < 0.01$)",
                    "Bias fairness metrics (e.g., $FNR_{protected\\_group} - FNR_{overall} < 0.02$)",
                    "Adversarial robustness (Healthcare-specific attacks)",
                    "Causal inference checks (clinical outcomes)",
                ],
                "monitoring": [
                    "Model drift (real-time)",
                    "Fairness metric drift (critical groups)",
                    "Outcome drift (real-time)",
                    "Override rates (by clinician/type)",
                    "Alert fatigue metrics (human feedback loop)",
                ],
                "incident_triggers": [
                    "Critical FNR increase (e.g., $FNR > 0.015$)",
                    "Sudden override rate surge ($>20\\%$ threshold)",
                    "Adverse patient outcome correlation identified",
                ],
            },
        },
        "LLM": {
            "Low": {
                "controls": ["Prompt engineering guidelines (Healthcare)", "Basic content moderation (Healthcare)"],
                "validation": ["Fluency and coherence (medical context)", "Relevance check (patient queries)"],
                "monitoring": ["Output quality (grammar, medical terminology)", "Query volume (trends)"],
                "incident_triggers": ["Inappropriate content generation (medical ethics breach)"],
            },
            "Medium": {
                "controls": [
                    "Prompt engineering guidelines (Healthcare)",
                    "Advanced content moderation (Healthcare)",
                    "Fact-checking integration (medical literature)",
                    "Data privacy controls (PHI)",
                ],
                "validation": [
                    "Hallucination rate evaluation (medical facts, $P(\\text{hallucination}) < 0.05$)",
                    "Bias in generated text (gender, ethnicity)",
                    "Context adherence (patient history)",
                ],
                "monitoring": [
                    "Hallucination rate drift",
                    "Bias metric drift (text generation)",
                    "Information accuracy (medical claims)",
                ],
                "incident_triggers": ["Increased hallucination (medical advice)", "Misinformation generation (patient safety risk)"],
            },
            "High": {
                "controls": [
                    "Prompt engineering guidelines (Healthcare)",
                    "Advanced content moderation (Healthcare)",
                    "Fact-checking integration (medical literature)",
                    "Data privacy controls (PHI)",
                    "Clinical verification workflow (human review for diagnoses)",
                    "Privacy-preserving methods (e.g., K-anonymity)",
                ],
                "validation": [
                    "Hallucination rate (strict thresholds, e.g., $P(\\text{hallucination}) < 0.005$ for diagnostic advice)",
                    "Bias in generated text for sensitive groups",
                    "Privacy leakage detection (PHI)",
                    "Clinical relevance and safety (adherence to guidelines)",
                ],
                "monitoring": [
                    "Hallucination rate drift (real-time, critical)",
                    "Privacy violation alerts (real-time)",
                    "Clinical override rates (for LLM suggestions)",
                    "Adherence to medical guidelines (automated checks)",
                ],
                "incident_triggers": ["Medical misinformation leading to harm", "Patient data breach (PHI exposure)", "Unsafe clinical recommendations generated"],
            },
        },
        "Agent": {
            "Low": {
                "controls": ["Action logging (Healthcare tasks)", "Basic authorization (Healthcare systems)"],
                "validation": ["Action efficacy (e.g., appointment scheduling accuracy)", "Boundary adherence (role limits)"],
                "monitoring": ["Action frequency", "Error rate (task completion)"],
                "incident_triggers": ["Unauthorized action attempts"],
            },
            "Medium": {
                "controls": [
                    "Action logging (Healthcare tasks)",
                    "Granular authorization (Healthcare systems)",
                    "Reversibility protocols (patient actions)",
                    "Autonomous action limits (e.g., dose adjustments)",
                ],
                "validation": [
                    "Complex task success rate (e.g., patient pathway optimization)",
                    "Unintended side effects (system interactions)",
                    "Reversal capability (action undo)",
                ],
                "monitoring": ["Autonomous action limits breached", "Error cascades (system-wide)", "Human intervention rates (agent-triggered)"],
                "incident_triggers": ["Agent taking unintended medical actions", "Significant error rate spike (impacting patient flow)"],
            },
            "High": {
                "controls": [
                    "Action logging (Healthcare tasks)",
                    "Granular authorization (Healthcare systems)",
                    "Reversibility protocols (patient actions)",
                    "Autonomous action limits (e.g., drug delivery)",
                    "Emergency stop mechanism (physical/digital)",
                    "Comprehensive audit trails (clinical decisions)",
                ],
                "validation": [
                    "Critical task success rate (e.g., $P(\\text{incorrect action}) < 0.001$ for life-critical functions)",
                    "Catastrophic failure modes (simulations)",
                    "Compliance with medical ethics and regulations (e.g., FDA)",
                ],
                "monitoring": [
                    "Unauthorized action attempts",
                    "Emergency stop activations",
                    "Audit trail integrity (real-time checks)",
                    "Deviation from pre-approved action space (e.g., off-label use)",
                ],
                "incident_triggers": ["Uncontrolled agent behavior (patient harm)", "Patient safety compromise (critical incident)", "System bypass attempts (security breach)"],
            },
        },
    }


def get_default_finance_control_templates() -> Dict[str, Any]:
    return {
        "ML": {
            "Low": {
                "controls": ["Data governance (Finance)", "Model documentation (Finance)"],
                "validation": ["Basic performance metrics (accuracy, $P(\\text{correct}) > 0.85$)", "Input data validation (financial ranges)"],
                "monitoring": ["Model drift", "Feature drift (economic indicators)"],
                "incident_triggers": ["Significant performance drop (e.g., accuracy below $0.8$)"],
            },
            "Medium": {
                "controls": [
                    "Data governance (Finance)",
                    "Model documentation (Finance)",
                    "Bias & fairness analysis (credit scoring)",
                    "Explainability (SHAP/LIME for loan officers)",
                ],
                "validation": [
                    "Advanced performance (Precision, Recall, F1 for fraud)",
                    "Bias fairness metrics (e.g., $0.8 \\le DIR \\le 1.25$ for protected groups in lending)",
                    "Explainability report consistency",
                ],
                "monitoring": ["Model drift (detailed)", "Feature drift", "Bias metric drift (by demographic)", "Explainability consistency"],
                "incident_triggers": ["Unfair outcomes for protected groups", "Inconsistent explanations leading to appeals"],
            },
            "High": {
                "controls": [
                    "Data governance (Finance)",
                    "Model documentation (Finance)",
                    "Bias & fairness analysis (credit scoring)",
                    "Explainability (SHAP/LIME for loan officers)",
                    "Auditability framework (SOX compliance)",
                    "Adherence to regulatory guidelines (e.g., CCPA, GDPR)",
                ],
                "validation": [
                    "Comprehensive performance (F1, AUROC, Precision@k for fraud, $FPR_{fraud} < 0.001$)",
                    "Bias fairness metrics (e.g., $0.8 \\le DIR \\le 1.25$ for all protected groups in credit decisions)",
                    "Robust explainability validation (counterfactuals)",
                    "Adversarial attack resistance (financial data)",
                ],
                "monitoring": [
                    "Model drift (real-time, market impact)",
                    "Feature drift (macro-economic)",
                    "Bias metric drift (critical groups)",
                    "Explainability consistency alerts",
                    "Approval rate drift",
                    "Exception volume (manual reviews)",
                ],
                "incident_triggers": [
                    "Regulatory non-compliance identified",
                    "Significant financial loss attributed to model",
                    "Public bias incident",
                    "Fraud miss rate spike (e.g., $FNR_{fraud} > 0.002$)",
                ],
            },
        },
        "LLM": {
            "Low": {
                "controls": ["Prompt guidelines (Finance)", "Content filtering (Financial terms)"],
                "validation": ["Response relevance (financial queries)", "Grammar/Spelling (professional tone)"],
                "monitoring": ["Output quality", "Usage patterns (customer queries)"],
                "incident_triggers": ["Inappropriate financial advice"],
            },
            "Medium": {
                "controls": [
                    "Prompt guidelines (Finance)",
                    "Content filtering (Financial terms)",
                    "Fact verification (financial data, market feeds)",
                    "Data privacy controls (PCI-DSS)",
                ],
                "validation": [
                    "Accuracy of financial data extraction ($P(\\text{error}) < 0.01$)",
                    "Hallucination rate (contextual, financial facts)",
                    "Privacy compliance check (customer data)",
                ],
                "monitoring": ["Hallucination rate (financial facts)", "Data privacy alerts", "Information accuracy (financial advice)"],
                "incident_triggers": ["Inaccurate financial advice provided", "Customer data leakage identified"],
            },
            "High": {
                "controls": [
                    "Prompt guidelines (Finance)",
                    "Content filtering (Financial terms)",
                    "Fact verification (financial data, market feeds)",
                    "Data privacy controls (PCI-DSS)",
                    "Human oversight for critical decisions (e.g., investment advice)",
                    "Audit trail for LLM outputs (regulatory)",
                ],
                "validation": [
                    "Accuracy of financial data extraction (strict, e.g., $P(\\text{error}) < 0.001$ for investment recommendations)",
                    "Hallucination rate (financial context, e.g., $P(\\text{hallucination}) < 0.005$ for market forecasts)",
                    "Privacy compliance (GDPR, CCPA, PCI-DSS)",
                    "Robustness to prompt injection (financial scams)",
                ],
                "monitoring": [
                    "Hallucination rate drift (financial facts, real-time)",
                    "Data privacy alerts (real-time)",
                    "Audit trail integrity (LLM decisions)",
                    "Regulatory compliance drift",
                ],
                "incident_triggers": ["Material financial error from LLM advice", "Regulatory breach (data handling)", "Significant reputational damage (public misinformation)"],
            },
        },
        "Agent": {
            "Low": {
                "controls": ["Action logging (Financial transactions)", "Access controls (Financial systems)"],
                "validation": ["Basic task completion (e.g., report generation)", "Security checks (API access)"],
                "monitoring": ["System uptime", "Transaction volume (reporting)"],
                "incident_triggers": ["System downtime impacting operations"],
            },
            "Medium": {
                "controls": [
                    "Action logging (Financial transactions)",
                    "Granular access controls (Financial systems)",
                    "Reversibility protocols (transaction rollback)",
                    "Transaction limits (individual/daily)",
                ],
                "validation": [
                    "Complex transaction success rate (e.g., fund transfers)",
                    "Fraud detection efficacy ($P(\\text{fraud detected}) > 0.9$)",
                    "Unintended market impact (simulations)",
                ],
                "monitoring": ["Transaction limit breaches", "Error rates in automated trades", "Fraud detection performance (real-time alerts)"],
                "incident_triggers": ["Unapproved transactions", "Automated fraud bypass (missed fraud)"],
            },
            "High": {
                "controls": [
                    "Action logging (Financial transactions)",
                    "Granular access controls (Financial systems)",
                    "Reversibility protocols (transaction rollback)",
                    "Transaction limits (individual/daily)",
                    "Real-time audit trails (all actions)",
                    "Circuit breakers for autonomous actions (market volatility)",
                ],
                "validation": [
                    "Critical transaction success rate (e.g., $P(\\text{fraudulent transaction}) < 0.0001$ for high-value transfers)",
                    "Market stability analysis (agent impact)",
                    "Compliance with financial regulations (e.g., Dodd-Frank, MiFID II)",
                ],
                "monitoring": [
                    "Unauthorized access attempts",
                    "Circuit breaker activations",
                    "Audit trail integrity (transaction logs)",
                    "Real-time P&L deviation (trading agents)",
                    "Compliance dashboard alerts",
                ],
                "incident_triggers": ["Market manipulation attempt by agent", "Major financial loss event", "System compromise leading to asset loss"],
            },
        },
    }


def get_default_sample_use_cases() -> List[Dict[str, Any]]:
    return [
        {
            "id": "HC-ML-001",
            "name": "Patient Triage and Prioritization (ML)",
            "description": "An ML model predicts patient acuity to prioritize care in an emergency room, aiming to reduce patient wait times while maintaining safety. A key risk is **false negatives** for high-acuity patients.",
            "sector": "Healthcare",
            "system_type": "ML",
            "risk_tier": "High",
        },
        {
            "id": "FI-LLM-002",
            "name": "Customer Service Chatbot (LLM)",
            "description": "An LLM-powered chatbot answers customer queries regarding bank services, providing information on account balances, transaction history, and general FAQs. The main risk is providing **inaccurate information** or **hallucinating** responses.",
            "sector": "Finance",
            "system_type": "LLM",
            "risk_tier": "Medium",
        },
        {
            "id": "HC-LLM-003",
            "name": "Clinical Decision Support (LLM)",
            "description": "An LLM provides diagnostic support and treatment recommendations to clinicians based on patient medical records and current research. A critical risk is **medical misinformation** or **hallucinations** leading to incorrect diagnoses or treatments.",
            "sector": "Healthcare",
            "system_type": "LLM",
            "risk_tier": "High",
        },
        {
            "id": "FI-Agent-004",
            "name": "Automated Fraud Detection Agent",
            "description": "An AI agent monitors transactions in real-time and autonomously blocks suspicious financial activities to prevent financial loss. The key risk is **missing actual fraud (false negatives)** or **blocking legitimate transactions (false positives)**.",
            "sector": "Finance",
            "system_type": "Agent",
            "risk_tier": "High",
        },
        {
            "id": "HC-Agent-005",
            "name": "Automated Medical Appointment Scheduler (Agent)",
            "description": "An AI agent manages and optimizes patient appointment scheduling, sending reminders and handling rescheduling requests. A primary risk is **incorrect scheduling** or **HIPAA compliance** violations.",
            "sector": "Healthcare",
            "system_type": "Agent",
            "risk_tier": "Low",
        },
    ]


# -----------------------------
# I/O helpers (data directory)
# -----------------------------

def ensure_data_files(data_dir: str = "data") -> Dict[str, str]:
    """
    Ensures the JSON files exist in `data_dir`.
    Returns a dict of filepaths.
    """
    os.makedirs(data_dir, exist_ok=True)

    paths = {
        "healthcare": os.path.join(data_dir, "healthcare_control_templates.json"),
        "finance": os.path.join(data_dir, "finance_control_templates.json"),
        "use_cases": os.path.join(data_dir, "sample_use_cases.json"),
    }

    if not os.path.exists(paths["healthcare"]):
        with open(paths["healthcare"], "w", encoding="utf-8") as f:
            json.dump(get_default_healthcare_control_templates(), f, indent=2)

    if not os.path.exists(paths["finance"]):
        with open(paths["finance"], "w", encoding="utf-8") as f:
            json.dump(get_default_finance_control_templates(), f, indent=2)

    if not os.path.exists(paths["use_cases"]):
        with open(paths["use_cases"], "w", encoding="utf-8") as f:
            json.dump(get_default_sample_use_cases(), f, indent=2)

    return paths


def load_control_templates(sector: str, data_dir: str = "data") -> Dict[str, Any]:
    """Loads control templates for a given sector from JSON files."""
    sector_norm = sector.strip().lower()
    ensure_data_files(data_dir)

    if sector_norm == "healthcare":
        path = os.path.join(data_dir, "healthcare_control_templates.json")
    elif sector_norm == "finance":
        path = os.path.join(data_dir, "finance_control_templates.json")
    else:
        raise ValueError(
            "Invalid sector specified. Choose 'Healthcare' or 'Finance'.")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sample_use_cases(data_dir: str = "data") -> List[Dict[str, Any]]:
    """Loads sample AI use cases from JSON files."""
    ensure_data_files(data_dir)
    path = os.path.join(data_dir, "sample_use_cases.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def select_use_case(use_case_id: str, all_cases: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Selects a specific use case by its ID."""
    for case in all_cases:
        if case.get("id") == use_case_id:
            return case
    return None


# -----------------------------
# Core generators
# -----------------------------

def generate_sector_playbook(
    sector: str,
    system_type: str,
    risk_tier: str,
    templates: Dict[str, Any],
) -> Dict[str, Any]:
    """Generates the sector-specific AI playbook based on inputs."""
    try:
        config = templates[system_type][risk_tier]
        return {
            "sector": sector,
            "system_type": system_type,
            "risk_tier": risk_tier,
            "controls": config.get("controls", []),
            "sector_emphasis": {
                "Healthcare": "Emphasis on False-Negative Risk, Clinical Override, Patient Safety, PHI Privacy.",
                "Finance": "Emphasis on Explainability, Bias & Disparate Impact, Auditability, Financial Stability, Data Security.",
            }.get(sector, "General AI risk management."),
        }
    except KeyError:
        return {"error": "Configuration not found for the given system type and risk tier."}


def generate_validation_checklist(
    use_case: Dict[str, Any],
    templates: Dict[str, Any],
) -> str:
    """Generates a detailed validation checklist with specific requirements and thresholds."""
    sector = use_case["sector"]
    system_type = use_case["system_type"]
    risk_tier = use_case["risk_tier"]

    try:
        config = templates[system_type][risk_tier]
    except KeyError:
        return "Error: Validation configuration not found."

    validation_items = config.get("validation", [])

    checklist = f"# Validation Checklist for {sector} {system_type} ({risk_tier} Risk)\n\n"
    checklist += f"**AI Initiative:** {use_case['name']} ({use_case['id']})\n"
    checklist += f"**Description:** {use_case['description']}\n\n"
    checklist += "This checklist outlines the required validation activities and acceptance thresholds for deployment.\n\n"

    for item in validation_items:
        checklist += f"- [ ] {item}\n"

    checklist += "\n### Key Acceptance Thresholds:\n"
    if sector == "Healthcare" and system_type == "ML" and risk_tier == "High":
        checklist += "- **False Negative Rate (FNR) for target conditions:** $FNR_{target\\_condition} < 0.01$ (e.g., for critical diagnoses)\n"
        checklist += "- **Bias in FNR across protected groups:** $\\left| FNR_{protected\\_group} - FNR_{overall} \\right| < 0.02$ \n"
        checklist += "- **Adversarial Robustness:** Model accuracy drop $< 5\\%$ under specified adversarial attacks.\n"
    elif sector == "Healthcare" and system_type == "LLM" and risk_tier == "High":
        checklist += "- **Hallucination Rate (Medical Advice):** $P(\\text{hallucination}) < 0.005$ for diagnostic support.\n"
        checklist += "- **Privacy Leakage:** $P(\\text{PHI exposure}) < 0.001$ in synthetic data generation or responses.\n"
    elif sector == "Finance" and system_type == "ML" and risk_tier == "High":
        checklist += "- **Disparate Impact Ratio (DIR) for credit decisions:** $0.8 \\le DIR \\le 1.25$ for all protected groups.\n"
        checklist += "- **False Positive Rate (FPR) for fraud detection:** $FPR_{fraud} < 0.001$ (to minimize legitimate transaction blocks).\n"
    elif sector == "Finance" and system_type == "LLM" and risk_tier == "High":
        checklist += "- **Financial Fact Accuracy:** $P(\\text{error}) < 0.001$ for extracted financial figures/advice.\n"
        checklist += "- **Prompt Injection Robustness:** Successful injection rate $< 0.01$ in red-teaming scenarios.\n"

    checklist += "\n### Evidence Requirements:\n"
    checklist += "- Detailed validation report including methodology, results, and statistical significance.\n"
    checklist += "- Dataset split documentation (training, validation, test, adversarial test sets).\n"
    checklist += "- Explainability analysis artifacts (e.g., SHAP values, LIME explanations).\n"

    return checklist


def generate_monitoring_kpis(use_case: Dict[str, Any], templates: Dict[str, Any]) -> List[str]:
    """Generates a list of monitoring KPIs."""
    try:
        return templates[use_case["system_type"]][use_case["risk_tier"]].get("monitoring", [])
    except KeyError:
        return []


def generate_incident_triggers(use_case: Dict[str, Any], templates: Dict[str, Any]) -> List[str]:
    """Generates a list of incident triggers."""
    try:
        return templates[use_case["system_type"]][use_case["risk_tier"]].get("incident_triggers", [])
    except KeyError:
        return []


def _extract_validation_requirements_only(validation_markdown: str) -> List[str]:
    """
    Extracts only the checklist portion (bullets) from the validation markdown.
    Keeps things simple/robust for your current formatting.
    """
    lines = validation_markdown.splitlines()
    out: List[str] = []
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("- [ ] "):
            out.append(ln.replace("- [ ] ", "").strip())
    return out


def create_config_snapshot(
    use_case: Dict[str, Any],
    playbook: Dict[str, Any],
    validation_markdown: str,
    kpis: List[str],
    triggers: List[str],
) -> Dict[str, Any]:
    """Combines all generated configuration into a single snapshot."""
    key = f"{use_case['sector']}_{use_case['system_type']}_{use_case['risk_tier']}"
    acceptance = {
        "Healthcare_ML_High": ["FNR < 0.01", "|FNR_group - FNR_overall| < 0.02"],
        "Healthcare_LLM_High": ["P(hallucination) < 0.005", "P(PHI exposure) < 0.001"],
        "Finance_ML_High": ["0.8 <= DIR <= 1.25", "FPR_fraud < 0.001"],
        "Finance_LLM_High": ["P(error) < 0.001 (financial facts)", "Prompt injection rate < 0.01"],
    }.get(key, [])

    return {
        "use_case_details": use_case,
        "ai_playbook": playbook,
        "validation_requirements": _extract_validation_requirements_only(validation_markdown),
        "acceptance_thresholds": acceptance,
        "monitoring_kpis": kpis,
        "incident_triggers": triggers,
        "generated_timestamp": datetime.now().isoformat(),
    }


def create_executive_summary(use_case: Dict[str, Any], snapshot: Dict[str, Any], ai_risk_lead: str = "Dr. Evelyn Reed") -> str:
    """Generates an executive summary in Markdown format."""
    summary = f"# Executive Summary: AI Risk Playbook for {use_case['name']}\n\n"
    summary += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
    summary += f"**AI Risk Lead:** {ai_risk_lead}\n\n"

    summary += "## 1. AI Initiative Overview\n"
    summary += f"**Name:** {use_case['name']}\n"
    summary += f"**ID:** {use_case['id']}\n"
    summary += f"**Description:** {use_case['description']}\n"
    summary += f"**Sector:** {use_case['sector']}\n"
    summary += f"**System Type:** {use_case['system_type']}\n"
    summary += f"**Risk Tier:** {use_case['risk_tier']}\n\n"

    summary += "## 2. Rationale for Tailored Controls\n"
    summary += (
        f"Given the **{use_case['risk_tier']} risk tier** and its deployment within the **{use_case['sector']} sector**, "
        "this AI system requires a highly specialized risk management framework. "
        f"For the '{use_case['name']}' system, the primary concerns include:\n"
    )

    if use_case["sector"] == "Healthcare":
        if use_case["system_type"] == "ML":
            summary += "- **Patient Safety:** Mitigation of **False Negatives**, with strong clinical override and human-in-the-loop.\n"
            summary += "- **Ethical Bias:** Fairness checks across demographic groups.\n"
            summary += "- **Data Privacy:** HIPAA-oriented PHI protection controls.\n"
        elif use_case["system_type"] == "LLM":
            summary += "- **Medical Accuracy & Safety:** Preventing hallucinations and unsafe recommendations.\n"
            summary += "- **PHI Protection:** Privacy leakage detection and PHI safeguards.\n"
    elif use_case["sector"] == "Finance":
        if use_case["system_type"] == "ML":
            summary += "- **Fairness & Integrity:** Bias/fairness analysis for high-stakes decisions (e.g., credit).\n"
            summary += "- **Explainability & Auditability:** Transparent rationale and compliance-aligned logging.\n"
        elif use_case["system_type"] == "LLM":
            summary += "- **Accuracy of Advice:** Fact verification and hallucination mitigation.\n"
            summary += "- **Regulatory Compliance:** PCI/GDPR/CCPA-oriented controls and audit trails.\n"

    summary += "\n## 3. Key Configuration Elements\n"
    summary += f"**Controls:** {', '.join(snapshot['ai_playbook'].get('controls', []))}\n"
    summary += f"**Validation Focus:** {', '.join(snapshot.get('validation_requirements', []))}\n"
    summary += f"**Acceptance Thresholds:** {'; '.join(snapshot.get('acceptance_thresholds', []))}\n"
    summary += f"**Monitoring KPIs:** {', '.join(snapshot.get('monitoring_kpis', []))}\n"
    summary += f"**Incident Triggers:** {', '.join(snapshot.get('incident_triggers', []))}\n\n"

    summary += (
        "This tailored playbook ensures comprehensive risk coverage, aligns with governance standards, "
        "and prepares the system for rigorous validation and operational oversight."
    )
    return summary


# -----------------------------
# Evidence manifest + hashing
# -----------------------------

def generate_file_hash(filepath: str) -> str:
    """Generates the SHA-256 hash for a given file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_evidence_manifest(output_directory: str, artifact_files: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generates an evidence manifest with SHA-256 hashes for all artifacts."""
    if artifact_files is None:
        artifact_files = [
            "sector_playbook.json",
            "validation_checklist.md",
            "monitoring_kpis.json",
            "incident_triggers.json",
            "executive_summary.md",
            "config_snapshot.json",
        ]

    manifest: Dict[str, Any] = {
        "manifest_timestamp": datetime.now().isoformat(), "artifacts": []}

    for filename in artifact_files:
        filepath = os.path.join(output_directory, filename)
        if os.path.exists(filepath):
            manifest["artifacts"].append(
                {
                    "filename": filename,
                    "filepath": filepath,
                    "sha256_hash": generate_file_hash(filepath),
                }
            )
        else:
            manifest["artifacts"].append(
                {
                    "filename": filename,
                    "filepath": filepath,
                    "status": "MISSING",
                    "notes": "File not found or not generated.",
                }
            )

    manifest_filename = os.path.join(
        output_directory, "evidence_manifest.json")
    with open(manifest_filename, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


# -----------------------------
# Top-level orchestration API
# -----------------------------

@dataclass(frozen=True)
class GenerationResult:
    use_case: Dict[str, Any]
    playbook: Dict[str, Any]
    validation_checklist_md: str
    monitoring_kpis: List[str]
    incident_triggers: List[str]
    config_snapshot: Dict[str, Any]
    executive_summary_md: str
    evidence_manifest: Dict[str, Any]
    output_dir: str


def generate_all_artifacts(
    use_case_id: str,
    data_dir: str = "data",
    output_dir: str = "generated_artifacts",
    ai_risk_lead: str = "Dr. Evelyn Reed",
    write_files: bool = True,
) -> GenerationResult:
    """
    Main function to be called from app.py.

    - Loads data
    - Selects use case
    - Generates playbook, validation checklist, KPIs, triggers
    - Generates snapshot + executive summary
    - Optionally writes artifacts to disk
    - Always returns everything as in-memory objects
    """
    all_cases = load_sample_use_cases(data_dir=data_dir)
    use_case = select_use_case(use_case_id, all_cases)
    if not use_case:
        raise ValueError(f"Use case with ID {use_case_id} not found.")

    templates = load_control_templates(use_case["sector"], data_dir=data_dir)

    playbook = generate_sector_playbook(
        sector=use_case["sector"],
        system_type=use_case["system_type"],
        risk_tier=use_case["risk_tier"],
        templates=templates,
    )
    validation_md = generate_validation_checklist(
        use_case=use_case, templates=templates)
    kpis = generate_monitoring_kpis(use_case=use_case, templates=templates)
    triggers = generate_incident_triggers(
        use_case=use_case, templates=templates)

    snapshot = create_config_snapshot(
        use_case=use_case,
        playbook=playbook,
        validation_markdown=validation_md,
        kpis=kpis,
        triggers=triggers,
    )

    executive_md = create_executive_summary(
        use_case=use_case, snapshot=snapshot, ai_risk_lead=ai_risk_lead)

    os.makedirs(output_dir, exist_ok=True)

    if write_files:
        # Write core artifacts
        with open(os.path.join(output_dir, "sector_playbook.json"), "w", encoding="utf-8") as f:
            json.dump(playbook, f, indent=2)

        with open(os.path.join(output_dir, "validation_checklist.md"), "w", encoding="utf-8") as f:
            f.write(validation_md)

        with open(os.path.join(output_dir, "monitoring_kpis.json"), "w", encoding="utf-8") as f:
            json.dump(kpis, f, indent=2)

        with open(os.path.join(output_dir, "incident_triggers.json"), "w", encoding="utf-8") as f:
            json.dump(triggers, f, indent=2)

        with open(os.path.join(output_dir, "config_snapshot.json"), "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)

        with open(os.path.join(output_dir, "executive_summary.md"), "w", encoding="utf-8") as f:
            f.write(executive_md)

        evidence = generate_evidence_manifest(output_dir)
    else:
        evidence = {"manifest_timestamp": datetime.now().isoformat(
        ), "artifacts": [], "notes": "write_files=False, no files hashed."}

    return GenerationResult(
        use_case=use_case,
        playbook=playbook,
        validation_checklist_md=validation_md,
        monitoring_kpis=kpis,
        incident_triggers=triggers,
        config_snapshot=snapshot,
        executive_summary_md=executive_md,
        evidence_manifest=evidence,
        output_dir=output_dir,
    )


# -----------------------------
# Optional CLI entrypoint
# -----------------------------

def main() -> None:
    """
    CLI mode:
      python source.py
      python source.py HC-ML-001
    """
    import sys

    use_case_id = sys.argv[1] if len(sys.argv) > 1 else "HC-ML-001"
    result = generate_all_artifacts(use_case_id=use_case_id, write_files=True)

    print(
        f"Selected AI Initiative: {result.use_case['name']} ({result.use_case['id']})")
    print(
        f"Sector: {result.use_case['sector']} | Type: {result.use_case['system_type']} | Risk: {result.use_case['risk_tier']}")
    print(f"Artifacts written to: {result.output_dir}")
    print(json.dumps(result.evidence_manifest, indent=2))


if __name__ == "__main__":
    main()
