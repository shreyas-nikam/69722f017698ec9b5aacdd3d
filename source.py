import pandas as pd
import json
import hashlib
import os
from datetime import datetime
# --- Synthetic Data Generation (instead of loading from files for demonstrative purposes) ---

# Define synthetic healthcare control templates
healthcare_control_templates = {
  "ML": {
    "Low": {
      "controls": ["Data governance (Healthcare)", "Model documentation (Healthcare)"],
      "validation": ["Basic performance metrics (accuracy, $P(\text{correct}) > 0.8$)", "Data quality check ($missing\_data < 5\%$)" ],
      "monitoring": ["Model drift (basic)", "Prediction integrity"],
      "incident_triggers": ["Significant performance drop (e.g., accuracy below $0.75$)"]
    },
    "Medium": {
      "controls": ["Data governance (Healthcare)", "Model documentation (Healthcare)", "Bias detection (demographics)", "Robustness testing (Healthcare specific)"],
      "validation": ["Advanced performance (AUC, F1, Sensitivity, Specificity)", "Bias fairness metrics (e.g., $FNR_{groupA} - FNR_{groupB} < 0.05$)", "Outlier detection"],
      "monitoring": ["Model drift (detailed)", "Fairness metric drift", "Outcome drift (e.g., re-hospitalization rates)"],
      "incident_triggers": ["Unacceptable bias detected", "Unexplained outcome changes", "High override rate ($>10\%$ of predictions)"]
    },
    "High": {
      "controls": ["Data governance (Healthcare)", "Model documentation (Healthcare)", "Bias detection (demographics)", "Robustness testing (Healthcare specific)", "Clinical override protocol", "Human-in-the-loop for critical decisions", "Explainability for clinicians", "Privacy-preserving data handling (HIPAA compliance)"],
      "validation": ["Comprehensive performance (Sensitivity, Specificity, $FNR_{target\_condition} < 0.01$)", "Bias fairness metrics (e.g., $FNR_{protected\_group} - FNR_{overall} < 0.02$)", "Adversarial robustness (Healthcare-specific attacks)", "Causal inference checks (clinical outcomes)"],
      "monitoring": ["Model drift (real-time)", "Fairness metric drift (critical groups)", "Outcome drift (real-time)", "Override rates (by clinician/type)", "Alert fatigue metrics (human feedback loop)"],
      "incident_triggers": ["Critical FNR increase (e.g., $FNR > 0.015$)", "Sudden override rate surge ($>20\%$ threshold)", "Adverse patient outcome correlation identified"]
    }
  },
  "LLM": {
    "Low": {
      "controls": ["Prompt engineering guidelines (Healthcare)", "Basic content moderation (Healthcare)"],
      "validation": ["Fluency and coherence (medical context)", "Relevance check (patient queries)"],
      "monitoring": ["Output quality (grammar, medical terminology)", "Query volume (trends)"],
      "incident_triggers": ["Inappropriate content generation (medical ethics breach)"]
    },
    "Medium": {
      "controls": ["Prompt engineering guidelines (Healthcare)", "Advanced content moderation (Healthcare)", "Fact-checking integration (medical literature)", "Data privacy controls (PHI)"],
      "validation": ["Hallucination rate evaluation (medical facts, $P(\text{hallucination}) < 0.05$)", "Bias in generated text (gender, ethnicity)", "Context adherence (patient history)"],
      "monitoring": ["Hallucination rate drift", "Bias metric drift (text generation)", "Information accuracy (medical claims)"],
      "incident_triggers": ["Increased hallucination (medical advice)", "Misinformation generation (patient safety risk)"]
    },
    "High": {
      "controls": ["Prompt engineering guidelines (Healthcare)", "Advanced content moderation (Healthcare)", "Fact-checking integration (medical literature)", "Data privacy controls (PHI)", "Clinical verification workflow (human review for diagnoses)", "Privacy-preserving methods (e.g., K-anonymity)"],
      "validation": ["Hallucination rate (strict thresholds, e.g., $P(\text{hallucination}) < 0.005$ for diagnostic advice)", "Bias in generated text for sensitive groups", "Privacy leakage detection (PHI)", "Clinical relevance and safety (adherence to guidelines)"],
      "monitoring": ["Hallucination rate drift (real-time, critical)", "Privacy violation alerts (real-time)", "Clinical override rates (for LLM suggestions)", "Adherence to medical guidelines (automated checks)"],
      "incident_triggers": ["Medical misinformation leading to harm", "Patient data breach (PHI exposure)", "Unsafe clinical recommendations generated"]
    }
  },
  "Agent": {
    "Low": {
      "controls": ["Action logging (Healthcare tasks)", "Basic authorization (Healthcare systems)"],
      "validation": ["Action efficacy (e.g., appointment scheduling accuracy)", "Boundary adherence (role limits)"],
      "monitoring": ["Action frequency", "Error rate (task completion)"],
      "incident_triggers": ["Unauthorized action attempts"]
    },
    "Medium": {
      "controls": ["Action logging (Healthcare tasks)", "Granular authorization (Healthcare systems)", "Reversibility protocols (patient actions)", "Autonomous action limits (e.g., dose adjustments)"],
      "validation": ["Complex task success rate (e.g., patient pathway optimization)", "Unintended side effects (system interactions)", "Reversal capability (action undo)"],
      "monitoring": ["Autonomous action limits breached", "Error cascades (system-wide)", "Human intervention rates (agent-triggered)"],
      "incident_triggers": ["Agent taking unintended medical actions", "Significant error rate spike (impacting patient flow)"]
    },
    "High": {
      "controls": ["Action logging (Healthcare tasks)", "Granular authorization (Healthcare systems)", "Reversibility protocols (patient actions)", "Autonomous action limits (e.g., drug delivery)", "Emergency stop mechanism (physical/digital)", "Comprehensive audit trails (clinical decisions)"],
      "validation": ["Critical task success rate (e.g., $P(\text{incorrect action}) < 0.001$ for life-critical functions)", "Catastrophic failure modes (simulations)", "Compliance with medical ethics and regulations (e.g., FDA)"],
      "monitoring": ["Unauthorized action attempts", "Emergency stop activations", "Audit trail integrity (real-time checks)", "Deviation from pre-approved action space (e.g., off-label use)"],
      "incident_triggers": ["Uncontrolled agent behavior (patient harm)", "Patient safety compromise (critical incident)", "System bypass attempts (security breach)"]
    }
  }
}

# Define synthetic finance control templates
finance_control_templates = {
  "ML": {
    "Low": {
      "controls": ["Data governance (Finance)", "Model documentation (Finance)"],
      "validation": ["Basic performance metrics (accuracy, $P(\text{correct}) > 0.85$)", "Input data validation (financial ranges)"],
      "monitoring": ["Model drift", "Feature drift (economic indicators)"],
      "incident_triggers": ["Significant performance drop (e.g., accuracy below $0.8$)"]
    },
    "Medium": {
      "controls": ["Data governance (Finance)", "Model documentation (Finance)", "Bias & fairness analysis (credit scoring)", "Explainability (SHAP/LIME for loan officers)"],
      "validation": ["Advanced performance (Precision, Recall, F1 for fraud)", "Bias fairness metrics (e.g., $0.8 \le DIR \le 1.25$ for protected groups in lending)", "Explainability report consistency"],
      "monitoring": ["Model drift (detailed)", "Feature drift", "Bias metric drift (by demographic)", "Explainability consistency"],
      "incident_triggers": ["Unfair outcomes for protected groups", "Inconsistent explanations leading to appeals"]
    },
    "High": {
      "controls": ["Data governance (Finance)", "Model documentation (Finance)", "Bias & fairness analysis (credit scoring)", "Explainability (SHAP/LIME for loan officers)", "Auditability framework (SOX compliance)", "Adherence to regulatory guidelines (e.g., CCPA, GDPR)"],
      "validation": ["Comprehensive performance (F1, AUROC, Precision@k for fraud, $FPR_{fraud} < 0.001$)", "Bias fairness metrics (e.g., $0.8 \le DIR \le 1.25$ for all protected groups in credit decisions)", "Robust explainability validation (counterfactuals)", "Adversarial attack resistance (financial data)"],
      "monitoring": ["Model drift (real-time, market impact)", "Feature drift (macro-economic)", "Bias metric drift (critical groups)", "Explainability consistency alerts", "Approval rate drift", "Exception volume (manual reviews)"],
      "incident_triggers": ["Regulatory non-compliance identified", "Significant financial loss attributed to model", "Public bias incident", "Fraud miss rate spike (e.g., $FNR_{fraud} > 0.002$)"]
    }
  },
  "LLM": {
    "Low": {
      "controls": ["Prompt guidelines (Finance)", "Content filtering (Financial terms)"],
      "validation": ["Response relevance (financial queries)", "Grammar/Spelling (professional tone)"],
      "monitoring": ["Output quality", "Usage patterns (customer queries)"],
      "incident_triggers": ["Inappropriate financial advice"]
    },
    "Medium": {
      "controls": ["Prompt guidelines (Finance)", "Content filtering (Financial terms)", "Fact verification (financial data, market feeds)", "Data privacy controls (PCI-DSS)"],
      "validation": ["Accuracy of financial data extraction ($P(\text{error}) < 0.01$)", "Hallucination rate (contextual, financial facts)", "Privacy compliance check (customer data)"],
      "monitoring": ["Hallucination rate (financial facts)", "Data privacy alerts", "Information accuracy (financial advice)"],
      "incident_triggers": ["Inaccurate financial advice provided", "Customer data leakage identified"]
    },
    "High": {
      "controls": ["Prompt guidelines (Finance)", "Content filtering (Financial terms)", "Fact verification (financial data, market feeds)", "Data privacy controls (PCI-DSS)", "Human oversight for critical decisions (e.g., investment advice)", "Audit trail for LLM outputs (regulatory)"],
      "validation": ["Accuracy of financial data extraction (strict, e.g., $P(\text{error}) < 0.001$ for investment recommendations)", "Hallucination rate (financial context, e.g., $P(\text{hallucination}) < 0.005$ for market forecasts)", "Privacy compliance (GDPR, CCPA, PCI-DSS)", "Robustness to prompt injection (financial scams)"],
      "monitoring": ["Hallucination rate drift (financial facts, real-time)", "Data privacy alerts (real-time)", "Audit trail integrity (LLM decisions)", "Regulatory compliance drift"],
      "incident_triggers": ["Material financial error from LLM advice", "Regulatory breach (data handling)", "Significant reputational damage (public misinformation)"]
    }
  },
  "Agent": {
    "Low": {
      "controls": ["Action logging (Financial transactions)", "Access controls (Financial systems)"],
      "validation": ["Basic task completion (e.g., report generation)", "Security checks (API access)"],
      "monitoring": ["System uptime", "Transaction volume (reporting)"],
      "incident_triggers": ["System downtime impacting operations"]
    },
    "Medium": {
      "controls": ["Action logging (Financial transactions)", "Granular access controls (Financial systems)", "Reversibility protocols (transaction rollback)", "Transaction limits (individual/daily)"],
      "validation": ["Complex transaction success rate (e.g., fund transfers)", "Fraud detection efficacy ($P(\text{fraud detected}) > 0.9$)", "Unintended market impact (simulations)"],
      "monitoring": ["Transaction limit breaches", "Error rates in automated trades", "Fraud detection performance (real-time alerts)"],
      "incident_triggers": ["Unapproved transactions", "Automated fraud bypass (missed fraud)"]
    },
    "High": {
      "controls": ["Action logging (Financial transactions)", "Granular access controls (Financial systems)", "Reversibility protocols (transaction rollback)", "Transaction limits (individual/daily)", "Real-time audit trails (all actions)", "Circuit breakers for autonomous actions (market volatility)"],
      "validation": ["Critical transaction success rate (e.g., $P(\text{fraudulent transaction}) < 0.0001$ for high-value transfers)", "Market stability analysis (agent impact)", "Compliance with financial regulations (e.g., Dodd-Frank, MiFID II)"],
      "monitoring": ["Unauthorized access attempts", "Circuit breaker activations", "Audit trail integrity (transaction logs)", "Real-time P&L deviation (trading agents)", "Compliance dashboard alerts"],
      "incident_triggers": ["Market manipulation attempt by agent", "Major financial loss event", "System compromise leading to asset loss"]
    }
  }
}

# Define synthetic sample use cases
sample_use_cases = [
  {
    "id": "HC-ML-001",
    "name": "Patient Triage and Prioritization (ML)",
    "description": "An ML model predicts patient acuity to prioritize care in an emergency room, aiming to reduce patient wait times while maintaining safety. A key risk is **false negatives** for high-acuity patients.",
    "sector": "Healthcare",
    "system_type": "ML",
    "risk_tier": "High"
  },
  {
    "id": "FI-LLM-002",
    "name": "Customer Service Chatbot (LLM)",
    "description": "An LLM-powered chatbot answers customer queries regarding bank services, providing information on account balances, transaction history, and general FAQs. The main risk is providing **inaccurate information** or **hallucinating** responses.",
    "sector": "Finance",
    "system_type": "LLM",
    "risk_tier": "Medium"
  },
  {
    "id": "HC-LLM-003",
    "name": "Clinical Decision Support (LLM)",
    "description": "An LLM provides diagnostic support and treatment recommendations to clinicians based on patient medical records and current research. A critical risk is **medical misinformation** or **hallucinations** leading to incorrect diagnoses or treatments.",
    "sector": "Healthcare",
    "system_type": "LLM",
    "risk_tier": "High"
  },
  {
    "id": "FI-Agent-004",
    "name": "Automated Fraud Detection Agent",
    "description": "An AI agent monitors transactions in real-time and autonomously blocks suspicious financial activities to prevent financial loss. The key risk is **missing actual fraud (false negatives)** or **blocking legitimate transactions (false positives)**.",
    "sector": "Finance",
    "system_type": "Agent",
    "risk_tier": "High"
  },
  {
    "id": "HC-Agent-005",
    "name": "Automated Medical Appointment Scheduler (Agent)",
    "description": "An AI agent manages and optimizes patient appointment scheduling, sending reminders and handling rescheduling requests. A primary risk is **incorrect scheduling** or **HIPAA compliance** violations.",
    "sector": "Healthcare",
    "system_type": "Agent",
    "risk_tier": "Low"
  }
]

# Save synthetic data to JSON files for consistency with requirement
os.makedirs("data", exist_ok=True)
with open("data/healthcare_control_templates.json", "w") as f:
    json.dump(healthcare_control_templates, f, indent=2)
with open("data/finance_control_templates.json", "w") as f:
    json.dump(finance_control_templates, f, indent=2)
with open("data/sample_use_cases.json", "w") as f:
    json.dump(sample_use_cases, f, indent=2)

# Load the control templates and use cases
def load_control_templates(sector):
    """Loads control templates for a given sector."""
    if sector.lower() == 'healthcare':
        with open("data/healthcare_control_templates.json", "r") as f:
            return json.load(f)
    elif sector.lower() == 'finance':
        with open("data/finance_control_templates.json", "r") as f:
            return json.load(f)
    else:
        raise ValueError("Invalid sector specified. Choose 'Healthcare' or 'Finance'.")

def load_sample_use_cases():
    """Loads sample AI use cases."""
    with open("data/sample_use_cases.json", "r") as f:
        return json.load(f)

# Execute data loading
all_use_cases = load_sample_use_cases()
print(f"Loaded {len(all_use_cases)} sample AI use cases.")
def select_use_case(use_case_id, all_cases):
    """Selects a specific use case by its ID."""
    for case in all_cases:
        if case["id"] == use_case_id:
            return case
    return None

# Evelyn selects a high-risk healthcare ML use case
selected_case_id = "HC-ML-001" # Patient Triage and Prioritization (ML)
selected_use_case = select_use_case(selected_case_id, all_use_cases)

if selected_use_case:
    print(f"Selected AI Initiative: {selected_use_case['name']} ({selected_use_case['id']})")
    print(f"Description: {selected_use_case['description']}")
    print(f"Sector: {selected_use_case['sector']}")
    print(f"System Type: {selected_use_case['system_type']}")
    print(f"Risk Tier: {selected_use_case['risk_tier']}")

    # Define the core parameters for the rules engine
    current_sector = selected_use_case['sector']
    current_system_type = selected_use_case['system_type']
    current_risk_tier = selected_use_case['risk_tier']
else:
    print(f"Use case with ID {selected_case_id} not found.")

# Store templates for the current sector
current_sector_templates = load_control_templates(current_sector)
def generate_sector_playbook(sector, system_type, risk_tier, templates):
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
                "Finance": "Emphasis on Explainability, Bias & Disparate Impact, Auditability, Financial Stability, Data Security."
            }.get(sector, "General AI risk management.")
        }
    except KeyError:
        return {"error": "Configuration not found for the given system type and risk tier."}

# Execute playbook generation
ai_playbook = generate_sector_playbook(current_sector, current_system_type, current_risk_tier, current_sector_templates)

# Create output directory if it doesn't exist
OUTPUT_DIR = "generated_artifacts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save the playbook to a JSON file
playbook_filename = os.path.join(OUTPUT_DIR, "sector_playbook.json")
with open(playbook_filename, "w") as f:
    json.dump(ai_playbook, f, indent=2)

print(f"Generated AI Playbook for {current_sector} {current_system_type} ({current_risk_tier} risk):")
print(json.dumps(ai_playbook, indent=2))
print(f"\nPlaybook saved to {playbook_filename}")
def generate_validation_checklist(sector, system_type, risk_tier, templates):
    """Generates a detailed validation checklist with specific requirements and thresholds."""
    try:
        config = templates[system_type][risk_tier]
        validation_items = config.get("validation", [])

        checklist_content = f"# Validation Checklist for {sector} {system_type} ({risk_tier} Risk)\n\n"
        checklist_content += f"**AI Initiative:** {selected_use_case['name']} ({selected_use_case['id']})\n"
        checklist_content += f"**Description:** {selected_use_case['description']}\n\n"
        checklist_content += "This checklist outlines the required validation activities and acceptance thresholds for deployment.\n\n"

        for item in validation_items:
            checklist_content += f"- [ ] {item}\n"

        checklist_content += "\n### Key Acceptance Thresholds:\n"
        if sector == "Healthcare" and system_type == "ML" and risk_tier == "High":
            checklist_content += "- **False Negative Rate (FNR) for target conditions:** $FNR_{target\_condition} < 0.01$ (e.g., for critical diagnoses)\n"
            checklist_content += "- **Bias in FNR across protected groups:** $\\left| FNR_{protected\_group} - FNR_{overall} \\right| < 0.02$ \n"
            checklist_content += "- **Adversarial Robustness:** Model accuracy drop $< 5\%$ under specified adversarial attacks.\n"
        elif sector == "Healthcare" and system_type == "LLM" and risk_tier == "High":
            checklist_content += "- **Hallucination Rate (Medical Advice):** $P(\\text{hallucination}) < 0.005$ for diagnostic support.\n"
            checklist_content += "- **Privacy Leakage:** $P(\\text{PHI exposure}) < 0.001$ in synthetic data generation or responses.\n"
        elif sector == "Finance" and system_type == "ML" and risk_tier == "High":
            checklist_content += "- **Disparate Impact Ratio (DIR) for credit decisions:** $0.8 \\le DIR \\le 1.25$ for all protected groups.\n"
            checklist_content += "- **False Positive Rate (FPR) for fraud detection:** $FPR_{fraud} < 0.001$ (to minimize legitimate transaction blocks).\n"
        elif sector == "Finance" and system_type == "LLM" and risk_tier == "High":
            checklist_content += "- **Financial Fact Accuracy:** $P(\\text{error}) < 0.001$ for extracted financial figures/advice.\n"
            checklist_content += "- **Prompt Injection Robustness:** Successful injection rate $< 0.01$ in red-teaming scenarios.\n"

        checklist_content += "\n### Evidence Requirements:\n"
        checklist_content += "- Detailed validation report including methodology, results, and statistical significance.\n"
        checklist_content += "- Dataset split documentation (training, validation, test, adversarial test sets).\n"
        checklist_content += "- Explainability analysis artifacts (e.g., SHAP values, LIME explanations).\n"

        return checklist_content
    except KeyError:
        return "Error: Validation configuration not found."

# Execute validation checklist generation
validation_checklist_content = generate_validation_checklist(current_sector, current_system_type, current_risk_tier, current_sector_templates)

# Save the validation checklist to a Markdown file
validation_filename = os.path.join(OUTPUT_DIR, "validation_checklist.md")
with open(validation_filename, "w") as f:
    f.write(validation_checklist_content)

print(validation_checklist_content)
print(f"\nValidation checklist saved to {validation_filename}")
def generate_monitoring_kpis(sector, system_type, risk_tier, templates):
    """Generates a list of monitoring KPIs."""
    try:
        config = templates[system_type][risk_tier]
        return config.get("monitoring", [])
    except KeyError:
        return []

def generate_incident_triggers(sector, system_type, risk_tier, templates):
    """Generates a list of incident triggers."""
    try:
        config = templates[system_type][risk_tier]
        return config.get("incident_triggers", [])
    except KeyError:
        return []

# Execute KPI and incident trigger generation
monitoring_kpis = generate_monitoring_kpis(current_sector, current_system_type, current_risk_tier, current_sector_templates)
incident_triggers = generate_incident_triggers(current_sector, current_system_type, current_risk_tier, current_sector_templates)

# Save KPIs to JSON
kpis_filename = os.path.join(OUTPUT_DIR, "monitoring_kpis.json")
with open(kpis_filename, "w") as f:
    json.dump(monitoring_kpis, f, indent=2)

# Save incident triggers to JSON
triggers_filename = os.path.join(OUTPUT_DIR, "incident_triggers.json")
with open(triggers_filename, "w") as f:
    json.dump(incident_triggers, f, indent=2)

print(f"Monitoring KPIs for {current_sector} {current_system_type} ({current_risk_tier} risk):\n{json.dumps(monitoring_kpis, indent=2)}")
print(f"\nIncident Triggers for {current_sector} {current_system_type} ({current_risk_tier} risk):\n{json.dumps(incident_triggers, indent=2)}")
print(f"\nMonitoring KPIs saved to {kpis_filename}")
print(f"Incident Triggers saved to {triggers_filename}")
def create_config_snapshot(use_case, playbook, validation, kpis, triggers):
    """Combines all generated configuration into a single snapshot."""
    snapshot = {
        "use_case_details": use_case,
        "ai_playbook": playbook,
        "validation_requirements": [item.strip() for item in validation.split("### Key Acceptance Thresholds:")[0].strip().split('\n') if item.strip()], # Extracting only the checklist items for the snapshot
        "acceptance_thresholds": {
            "Healthcare_ML_High": ["FNR < 0.01", "|FNR_group - FNR_overall| < 0.02"],
            "Healthcare_LLM_High": ["P(hallucination) < 0.005", "P(PHI exposure) < 0.001"],
            "Finance_ML_High": ["0.8 <= DIR <= 1.25", "FPR_fraud < 0.001"],
            "Finance_LLM_High": ["P(error) < 0.001 (financial facts)", "Prompt injection rate < 0.01"]
        }.get(f"{use_case['sector']}_{use_case['system_type']}_{use_case['risk_tier']}", []),
        "monitoring_kpis": kpis,
        "incident_triggers": triggers,
        "generated_timestamp": datetime.now().isoformat()
    }
    return snapshot

def create_executive_summary(use_case, snapshot):
    """Generates an executive summary in Markdown format."""
    summary = f"# Executive Summary: AI Risk Playbook for {use_case['name']}\n\n"
    summary += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
    summary += f"**AI Risk Lead:** Dr. Evelyn Reed\n\n"
    summary += f"## 1. AI Initiative Overview\n"
    summary += f"**Name:** {use_case['name']}\n"
    summary += f"**ID:** {use_case['id']}\n"
    summary += f"**Description:** {use_case['description']}\n"
    summary += f"**Sector:** {use_case['sector']}\n"
    summary += f"**System Type:** {use_case['system_type']}\n"
    summary += f"**Risk Tier:** {use_case['risk_tier']}\n\n"

    summary += f"## 2. Rationale for Tailored Controls\n"
    summary += f"Given the **{use_case['risk_tier']} risk tier** and its deployment within the **{use_case['sector']} sector**, this AI system requires a highly specialized risk management framework. For the '{use_case['name']}' system, the primary concerns include: \n"

    if use_case['sector'] == 'Healthcare':
        if use_case['system_type'] == 'ML':
            summary += "- **Patient Safety:** Mitigation of **False Negatives** (missing critical conditions), ensuring robust `Clinical override protocol` and `Human-in-the-loop` mechanisms. The target for `False Negative Rate (FNR)` is extremely strict, $FNR < 0.01$, reflecting the direct impact on patient health.\n"
            summary += "- **Ethical Bias:** Ensuring fairness across demographic groups, with specific validation for `Bias fairness metrics` to maintain $\\left| FNR_{protected\\_group} - FNR_{overall} \\right| < 0.02$.\n"
            summary += "- **Data Privacy:** Strict adherence to `Privacy-preserving data handling (HIPAA compliance)` for Protected Health Information (PHI).\n"
        elif use_case['system_type'] == 'LLM':
            summary += "- **Medical Accuracy & Safety:** Preventing **hallucinations** that could lead to medical misinformation. Validation includes strict thresholds like $P(\\text{hallucination}) < 0.005$ for diagnostic support.\n"
            summary += "- **PHI Protection:** Controls around `Data privacy controls (PHI)` and `Privacy leakage detection` are critical.\n"
    elif use_case['sector'] == 'Finance':
        if use_case['system_type'] == 'ML':
            summary += "- **Financial Integrity & Fairness:** Addressing `Bias & fairness analysis` for critical decisions (e.g., credit scoring) with `Disparate Impact Ratio (DIR)` targets ($0.8 \\le DIR \\le 1.25$).\n"
            summary += "- **Explainability & Auditability:** Ensuring `Explainability` for regulatory compliance and `Auditability framework` for transparent decision-making. Strict `False Positive Rate (FPR)` targets ($FPR_{fraud} < 0.001$) are set for fraud detection to minimize blocking legitimate transactions.\n"
        elif use_case['system_type'] == 'LLM':
            summary += "- **Accuracy of Financial Advice:** Mitigating `hallucinations` in financial contexts and ensuring `fact verification (financial data)`. Validation targets like $P(\\text{error}) < 0.001$ for financial figures are implemented.\n"
            summary += "- **Regulatory Compliance:** Adherence to `Data privacy controls (PCI-DSS)` and `Audit trail for LLM outputs`.\n"

    summary += f"\n## 3. Key Configuration Elements\n"
    # Adjusted to extract content without bullet point/checkbox syntax for cleanliness in summary
    # The validation_requirements from snapshot is already processed to remove checkboxes, just joining them.
    cleaned_validation_focus = [item.strip('- [] ') for item in snapshot['validation_requirements'] if item.strip('- [] ')]

    summary += f"**Controls:** {', '.join(snapshot['ai_playbook']['controls'])}\n"
    summary += f"**Validation Focus:** {', '.join(cleaned_validation_focus)}\n"
    summary += f"**Acceptance Thresholds:** {'; '.join(snapshot['acceptance_thresholds'])}\n"
    summary += f"**Monitoring KPIs:** {', '.join(snapshot['monitoring_kpis'])}\n"
    summary += f"**Incident Triggers:** {', '.join(snapshot['incident_triggers'])}\n\n"

    summary += f"This tailored playbook ensures comprehensive risk coverage, aligns with Global Innovations Inc.'s governance standards, and prepares the system for rigorous model validation and operational oversight."

    return summary

# Execute snapshot and executive summary generation
config_snapshot = create_config_snapshot(
    selected_use_case,
    ai_playbook,
    validation_checklist_content,
    monitoring_kpis,
    incident_triggers
)

executive_summary_content = create_executive_summary(selected_use_case, config_snapshot)

# Save the config snapshot to JSON
snapshot_filename = os.path.join(OUTPUT_DIR, "config_snapshot.json")
with open(snapshot_filename, "w") as f:
    json.dump(config_snapshot, f, indent=2)

# Save the executive summary to Markdown
summary_filename = os.path.join(OUTPUT_DIR, "executive_summary.md")
with open(summary_filename, "w") as f:
    f.write(executive_summary_content)

print(f"Generated Configuration Snapshot for {selected_use_case['name']}:\n{json.dumps(config_snapshot, indent=2)}")
print(f"\nConfiguration snapshot saved to {snapshot_filename}")
print(f"\n--- Executive Summary ---\n{executive_summary_content}")
print(f"\nExecutive summary saved to {summary_filename}")
def generate_file_hash(filepath):
    """Generates the SHA-256 hash for a given file."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)  # Read in 8KB chunks
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def generate_evidence_manifest(output_directory):
    """Generates an evidence manifest with SHA-256 hashes for all artifacts."""
    manifest = {
        "manifest_timestamp": datetime.now().isoformat(),
        "artifacts": []
    }

    # List of expected artifact files
    artifact_files = [
        "sector_playbook.json",
        "validation_checklist.md",
        "monitoring_kpis.json",
        "incident_triggers.json",
        "executive_summary.md",
        "config_snapshot.json"
    ]

    for filename in artifact_files:
        filepath = os.path.join(output_directory, filename)
        if os.path.exists(filepath):
            file_hash = generate_file_hash(filepath)
            manifest["artifacts"].append({
                "filename": filename,
                "filepath": filepath,
                "sha256_hash": file_hash
            })
        else:
            manifest["artifacts"].append({
                "filename": filename,
                "filepath": filepath,
                "status": "MISSING",
                "notes": "File not found or not generated."
            })

    manifest_filename = os.path.join(output_directory, "evidence_manifest.json")
    with open(manifest_filename, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest

# Execute evidence manifest generation
evidence_manifest = generate_evidence_manifest(OUTPUT_DIR)

print(f"\nGenerated Evidence Manifest:\n{json.dumps(evidence_manifest, indent=2)}")
print(f"\nEvidence manifest saved to {os.path.join(OUTPUT_DIR, 'evidence_manifest.json')}")
print("--- Review of Generated Artifacts ---")
print(f"Output directory: {OUTPUT_DIR}\n")

# List all files in the output directory
generated_files = os.listdir(OUTPUT_DIR)
for filename in generated_files:
    filepath = os.path.join(OUTPUT_DIR, filename)
    print(f"- {filename} (Size: {os.path.getsize(filepath)} bytes)")

print("\n--- Workflow Complete ---")
print(f"Dr. Evelyn Reed has successfully generated a comprehensive AI Risk Playbook for the '{selected_use_case['name']}' initiative, tailored for the {selected_use_case['sector']} sector and its {selected_use_case['risk_tier']} risk tier.")
print("All artifacts, including a detailed executive summary and an audit evidence manifest, have been created.")
print("This ensures proactive governance and provides a clear path for Model Validators and Domain AI Leads to manage the AI system effectively.")