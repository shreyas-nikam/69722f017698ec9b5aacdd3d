# QuLab: Lab 13: Sector Playbook Builder (Healthcare & Finance)

![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

## Project Title and Description

The **QuLab: Lab 13: Sector Playbook Builder** is a Streamlit application designed to assist AI Risk Leads, such as Dr. Evelyn Reed at Global Innovations Inc., in dynamically generating sector-specific AI risk management playbooks. In regulated industries like Healthcare and Finance, ensuring AI systems meet stringent regulatory and ethical standards is paramount. This application provides a systematic, transparent, and auditable approach for defining appropriate controls, validation rigor, and monitoring requirements tailored to any given AI application's sector, system type (e.g., ML, LLM, AI Agent), and inherent risk tier.

The application simulates a workflow where a user configures AI risk requirements, observes how controls adapt in real-time, and generates comprehensive documentation to justify tailored risk mitigations. This proactive governance approach ensures efficient resource allocation, clear communication with Domain AI Leads and Model Validators, and robust auditability for compliance.

## Features

This application offers a guided workflow through several key stages of AI risk playbook generation:

*   **Dynamic Template & Use Case Loading**: Loads pre-defined AI control templates and sample use cases, encapsulating standardized risk management policies tailored for various sector, system type, and risk tier combinations.
*   **AI Initiative Selection Wizard**: Allows users to select a specific AI use case, which automatically configures the system's `sector`, `system_type`, and `risk_tier`, forming the foundation for dynamic rules engine.
*   **Sector-Specific AI Control Playbook Generation**: Dynamically generates a detailed AI control playbook (`sector_playbook.json`) outlining foundational risk management strategies and controls specifically mandated for the selected sector, system type, and risk level.
*   **Tailored Validation Checklist Builder**: Creates a `validation_checklist.md` with specific, domain-relevant requirements and acceptance thresholds. This includes quantitative measures like False Negative Rates (FNR) and bias fairness metrics (e.g., $|FNR_{\text{protected\_group}} - FNR_{\text{overall}}|$), ensuring rigorous evaluation.
*   **Monitoring KPI & Incident Trigger Designer**: Defines `monitoring_kpis.json` and `incident_triggers.json` to ensure continuous post-deployment safety and performance. Metrics like `Outcome drift`, `Override rates`, and `Alert fatigue` are included to provide clear signals for intervention.
*   **Comprehensive Artifact Export Panel**:
    *   **Configuration Snapshot (`config_snapshot.json`)**: Consolidates all derived controls, validation criteria, and monitoring details into a single, comprehensive configuration summary.
    *   **Executive Summary (`executive_summary.md`)**: Generates a concise, high-level summary justifying the AI system's governance posture to senior leadership and cross-functional teams.
    *   **Evidence Manifest (`evidence_manifest.json`)**: Creates an auditable log of all generated files, including their SHA-256 hashes, to ensure immutability and verify file integrity.
    *   **One-Click ZIP Download**: Allows users to download all generated artifacts as a single ZIP archive for easy sharing and record-keeping.
*   **Persona Selection**: Enables switching between different user personas (e.g., AI Risk Lead, Domain AI Lead, Model Validator) to simulate varied stakeholder perspectives.

## Getting Started

Follow these instructions to set up and run the Streamlit application on your local machine.

### Prerequisites

*   Python 3.8 or higher

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/quolab-lab13-ai-playbook.git
    cd quolab-lab13-ai-playbook
    ```
    *(Replace `your-username/quolab-lab13-ai-playbook` with the actual repository path)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file in the root of your project with the following content:
    ```
    streamlit
    ```
    Then, install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ensure `source.py` is present:**
    The application relies on a `source.py` file in the same directory for its core logic, including data loading and playbook generation functions. Make sure this file is available alongside `app.py`. Its content is not provided here but would contain functions like `load_sample_use_cases`, `generate_sector_playbook`, etc.

## Usage

1.  **Run the Streamlit application:**
    From the project root directory, execute:
    ```bash
    streamlit run app.py
    ```
    This will open the application in your default web browser. If it doesn't open automatically, you can navigate to `http://localhost:8501`.

2.  **Navigate the application:**
    *   Use the **sidebar** to navigate between the different stages of the playbook generation process: "Sector & Use-Case Wizard", "Control Selection Preview", "Validation Checklist Builder", "Monitoring KPI Designer", and "Export Panel".
    *   **"Sector & Use-Case Wizard"**: Start by clicking "Load AI Control Templates & Use Cases", then select an AI Use Case from the dropdown. Click "Generate Playbook Components".
    *   **Subsequent Pages**: Explore the generated `AI Playbook`, `Validation Checklist`, `Monitoring KPIs`, and `Incident Triggers` by navigating to their respective pages.
    *   **"Export Panel"**: Click "Generate All Final Artifacts" to create the `config_snapshot.json`, `executive_summary.md`, and `evidence_manifest.json`. You can then download all these artifacts as a single ZIP file.

## Project Structure

```
.
├── app.py                     # Main Streamlit application file
├── source.py                  # Contains core business logic (data loading, playbook generation functions)
├── requirements.txt           # List of Python dependencies
├── README.md                  # This README file
└── reports/                   # Directory for generated output reports (created by the app)
    └── session13/
        └── [run_id]/          # Timestamped directory for each session's artifacts
            ├── sector_playbook.json
            ├── validation_checklist.md
            ├── monitoring_kpis.json
            ├── incident_triggers.json
            ├── config_snapshot.json
            ├── executive_summary.md
            └── evidence_manifest.json
```

## Technology Stack

*   **Python**: The primary programming language.
*   **Streamlit**: The framework used for building the interactive web application.
*   **Standard Python Libraries**: `os`, `json`, `hashlib`, `zipfile`, `io`, `datetime` for file operations, data handling, hashing, and archiving.
*   **`source.py`**: A custom module encapsulating the application's core logic and template data.

## Contributing

Contributions are welcome! If you'd like to improve this project, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add new feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
*(If you do not have a LICENSE file, you should create one or state "Proprietary" if for internal use only)*

## Contact

For any questions or suggestions, please contact:

*   **Organization**: QuantUniversity
*   **GitHub**: [https://github.com/quantuniversity](https://github.com/quantuniversity)
*   **Email**: info@quantuniversity.com
