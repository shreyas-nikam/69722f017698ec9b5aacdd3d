
import pytest
from unittest.mock import patch, MagicMock, mock_open
from streamlit.testing.v1 import AppTest
import json
import os
import io
from datetime import datetime

# Mock data for source.py functions
MOCK_USE_CASES = [
    {"id": "UC001", "name": "Fraud Detection", "description": "Detects fraudulent transactions.", "sector": "Finance", "system_type": "Machine Learning", "risk_tier": "High"},
    {"id": "UC002", "name": "Patient Diagnosis", "description": "Assists in diagnosing diseases.", "sector": "Healthcare", "system_type": "LLM", "risk_tier": "Critical"},
    {"id": "UC003", "name": "Credit Scoring", "description": "Calculates creditworthiness.", "sector": "Finance", "system_type": "Machine Learning", "risk_tier": "Medium"},
]

MOCK_CONTROL_TEMPLATES = {
    "Finance": {"controls": ["Financial Control 1", "Financial Control 2"]},
    "Healthcare": {"controls": ["Healthcare Control 1", "Healthcare Control 2"]},
}

MOCK_PLAYBOOK = {"playbook_data": "Generated playbook content for UC001"}
MOCK_VALIDATION_CHECKLIST = "Generated validation checklist content for UC001"
MOCK_MONITORING_KPIS = {"kpis": ["KPI A", "KPI B"]}
MOCK_INCIDENT_TRIGGERS = {"triggers": ["Trigger X", "Trigger Y"]}
MOCK_CONFIG_SNAPSHOT = {"snapshot_key": "snapshot_value"}
MOCK_EXECUTIVE_SUMMARY = "This is a mock executive summary."
# Reflects the expected files that would be generated and included in the evidence manifest
MOCK_EVIDENCE_MANIFEST = {
    "sector_playbook.json": "hash_playbook",
    "validation_checklist.md": "hash_checklist",
    "monitoring_kpis.json": "hash_kpis",
    "incident_triggers.json": "hash_triggers",
    "config_snapshot.json": "hash_snapshot",
    "executive_summary.md": "hash_summary"
}

@pytest.fixture(autouse=True)
def mock_external_dependencies():
    """
    Mocks external dependencies like source.py functions and file system operations.
    """
    m_open = mock_open()

    # Mock os.walk to simulate files being present in the output_dir_path
    def mock_os_walk_side_effect(path):
        # Simulate files created by generate_final_artifacts_callback for zipping
        mock_files = [
            "sector_playbook.json",
            "validation_checklist.md",
            "monitoring_kpis.json",
            "incident_triggers.json",
            "config_snapshot.json",
            "executive_summary.md",
        ]
        return [(path, [], mock_files)] # Yield once for the base directory

    with patch("source.load_sample_use_cases", return_value=MOCK_USE_CASES), \
         patch("source.select_use_case", side_effect=lambda id, ucs: next((uc for uc in ucs if uc['id'] == id), None)), \
         patch("source.load_control_templates", side_effect=lambda sector: MOCK_CONTROL_TEMPLATES.get(sector, {})), \
         patch("source.generate_sector_playbook", return_value=MOCK_PLAYBOOK), \
         patch("source.generate_validation_checklist", return_value=MOCK_VALIDATION_CHECKLIST), \
         patch("source.generate_monitoring_kpis", return_value=MOCK_MONITORING_KPIS), \
         patch("source.generate_incident_triggers", return_value=MOCK_INCIDENT_TRIGGERS), \
         patch("source.create_config_snapshot", return_value=MOCK_CONFIG_SNAPSHOT), \
         patch("source.create_executive_summary", return_value=MOCK_EXECUTIVE_SUMMARY), \
         patch("source.generate_evidence_manifest", return_value=MOCK_EVIDENCE_MANIFEST), \
         patch("os.makedirs"), \
         patch("os.path.join", side_effect=os.path.join), \
         patch("os.path.relpath", side_effect=os.path.relpath), \
         patch("os.walk", side_effect=mock_os_walk_side_effect), \
         patch("builtins.open", m_open): # Mock open for all file system operations
        yield m_open # Yield the mock_open object to inspect calls to it in tests

def test_initial_app_load():
    """
    Tests the initial loading of the Streamlit application and default state.
    """
    at = AppTest.from_file("app.py").run()

    # Verify initial page configuration and title
    assert at.title[0].value == "QuLab: Lab 13: Sector Playbook Builder (Healthcare & Finance)"

    # Verify initial session state values
    assert at.session_state.current_page == "Sector & Use-Case Wizard"
    assert at.session_state.persona == "AI Risk Lead (Evelyn Reed)"
    assert not at.session_state.data_loaded
    assert not at.session_state.all_use_cases
    assert at.session_state.selected_use_case_display is None
    assert at.session_state.selected_use_case is None
    assert not at.session_state.playbook_components_generated
    assert not at.session_state.final_artifacts_generated

    # Verify initial UI elements on "Sector & Use-Case Wizard" page
    assert at.button[0].label == "Load AI Control Templates & Use Cases"
    assert at.button[0].disabled is False # Button should be enabled initially
    assert at.success == [] # No success message initially

def test_load_data_and_select_use_case():
    """
    Tests loading AI control templates and use cases, and selecting a different use case.
    """
    at = AppTest.from_file("app.py").run()

    # Click "Load AI Control Templates & Use Cases" button (button[0])
    at.button[0].click().run()

    # Verify data is loaded and success message
    assert at.session_state.data_loaded
    assert len(at.session_state.all_use_cases) == len(MOCK_USE_CASES)
    assert at.success[0].value == "AI Control Templates and Use Cases Loaded!"
    assert at.button[0].disabled is True # Button should be disabled after loading

    # Verify a use case is pre-selected and displayed
    assert at.session_state.selected_use_case_display == f"{MOCK_USE_CASES[0]['name']} ({MOCK_USE_CASES[0]['id']})"
    assert at.session_state.selected_use_case == MOCK_USE_CASES[0]
    assert at.session_state.current_sector == MOCK_USE_CASES[0]['sector']
    assert at.session_state.current_system_type == MOCK_USE_CASES[0]['system_type']
    assert at.session_state.current_risk_tier == MOCK_USE_CASES[0]['risk_tier']
    assert at.session_state.current_sector_templates == MOCK_CONTROL_TEMPLATES.get(MOCK_USE_CASES[0]['sector'])

    # Change selected use case using the selectbox (selectbox[2])
    second_use_case_display = f"{MOCK_USE_CASES[1]['name']} ({MOCK_USE_CASES[1]['id']})"
    at.selectbox[2].set_value(second_use_case_display).run()

    assert at.session_state.selected_use_case_display == second_use_case_display
    assert at.session_state.selected_use_case == MOCK_USE_CASES[1]
    assert at.session_state.current_sector == MOCK_USE_CASES[1]['sector']
    assert at.session_state.current_system_type == MOCK_USE_CASES[1]['system_type']
    assert at.session_state.current_risk_tier == MOCK_USE_CASES[1]['risk_tier']
    assert at.session_state.current_sector_templates == MOCK_CONTROL_TEMPLATES.get(MOCK_USE_CASES[1]['sector'])

    # Verify "Generate Playbook Components" button (button[1]) is enabled
    assert at.button[1].label == "Generate Playbook Components"
    assert at.button[1].disabled is False

def test_generate_playbook_components():
    """
    Tests the generation of playbook components after data is loaded and a use case is selected.
    """
    at = AppTest.from_file("app.py").run()
    at.button[0].click().run() # Load data
    at.button[1].click().run() # Click "Generate Playbook Components" (button[1])

    assert at.session_state.playbook_components_generated
    assert at.session_state.ai_playbook == MOCK_PLAYBOOK
    assert at.session_state.validation_checklist_content == MOCK_VALIDATION_CHECKLIST
    assert at.session_state.monitoring_kpis == MOCK_MONITORING_KPIS
    assert at.session_state.incident_triggers == MOCK_INCIDENT_TRIGGERS
    assert at.success[1].value == "Playbook components generated!" # Check the second success message
    assert at.button[1].disabled is True # Button should be disabled after generation

def test_navigation_and_control_selection_preview_page():
    """
    Tests navigation to "Control Selection Preview" and verifies displayed playbook content.
    """
    at = AppTest.from_file("app.py").run()
    at.button[0].click().run() # Load data
    at.button[1].click().run() # Generate playbook components

    # Navigate to "Control Selection Preview" using the sidebar selectbox (selectbox[0])
    at.selectbox[0].set_value("Control Selection Preview").run()

    assert at.session_state.current_page == "Control Selection Preview"
    assert "Sector-Specific AI Control Playbook Preview" in at.markdown[0].value
    assert at.json[0].value == MOCK_PLAYBOOK # Verify playbook content is displayed

def test_control_selection_preview_page_warning_if_not_generated():
    """
    Tests that "Control Selection Preview" shows a warning if components are not generated.
    """
    at = AppTest.from_file("app.py").run()
    # No components generated
    at.selectbox[0].set_value("Control Selection Preview").run()
    assert at.warning[0].value == "Please go to 'Sector & Use-Case Wizard' and generate playbook components first."

def test_navigation_and_validation_checklist_builder_page():
    """
    Tests navigation to "Validation Checklist Builder" and verifies displayed checklist content.
    """
    at = AppTest.from_file("app.py").run()
    at.button[0].click().run() # Load data
    at.button[1].click().run() # Generate playbook components

    # Navigate to "Validation Checklist Builder"
    at.selectbox[0].set_value("Validation Checklist Builder").run()

    assert at.session_state.current_page == "Validation Checklist Builder"
    assert "Validation Checklist with Specific Requirements and Thresholds" in at.markdown[0].value
    assert at.markdown[5].value == MOCK_VALIDATION_CHECKLIST # Corrected markdown index

def test_validation_checklist_page_warning_if_not_generated():
    """
    Tests that "Validation Checklist Builder" shows a warning if components are not generated.
    """
    at = AppTest.from_file("app.py").run()
    at.selectbox[0].set_value("Validation Checklist Builder").run()
    assert at.warning[0].value == "Please go to 'Sector & Use-Case Wizard' and generate playbook components first."

def test_navigation_and_monitoring_kpi_designer_page():
    """
    Tests navigation to "Monitoring KPI Designer" and verifies displayed KPIs and incident triggers.
    """
    at = AppTest.from_file("app.py").run()
    at.button[0].click().run() # Load data
    at.button[1].click().run() # Generate playbook components

    # Navigate to "Monitoring KPI Designer"
    at.selectbox[0].set_value("Monitoring KPI Designer").run()

    assert at.session_state.current_page == "Monitoring KPI Designer"
    assert "Monitoring KPIs and Incident Triggers" in at.markdown[0].value
    assert at.json[0].value == MOCK_MONITORING_KPIS
    assert at.json[1].value == MOCK_INCIDENT_TRIGGERS

def test_monitoring_kpi_page_warning_if_not_generated():
    """
    Tests that "Monitoring KPI Designer" shows a warning if components are not generated.
    """
    at = AppTest.from_file("app.py").run()
    at.selectbox[0].set_value("Monitoring KPI Designer").run()
    assert at.warning[0].value == "Please go to 'Sector & Use-Case Wizard' and generate playbook components first."

def test_generate_final_artifacts(mock_external_dependencies):
    """
    Tests the generation of all final artifacts in the "Export Panel" page.
    """
    at = AppTest.from_file("app.py").run()
    at.button[0].click().run() # Load data
    at.button[1].click().run() # Generate playbook components

    # Navigate to "Export Panel"
    at.selectbox[0].set_value("Export Panel").run()

    # Click "Generate All Final Artifacts" button (button[0] on this page)
    at.button[0].click().run()

    assert at.session_state.final_artifacts_generated
    assert at.session_state.config_snapshot == MOCK_CONFIG_SNAPSHOT
    assert at.session_state.executive_summary_content == MOCK_EXECUTIVE_SUMMARY
    assert at.session_state.evidence_manifest == MOCK_EVIDENCE_MANIFEST
    assert at.success[0].value == "All final artifacts generated successfully!"

    # Verify displayed content on the page
    assert at.json[0].value == MOCK_CONFIG_SNAPSHOT
    assert at.markdown[13].value == MOCK_EXECUTIVE_SUMMARY # Corrected markdown index for summary
    assert at.json[1].value == MOCK_EVIDENCE_MANIFEST # Corrected json index for manifest

    # Verify download button exists and its properties
    assert at.download_button[0].label == "Download All Artifacts as ZIP"
    assert at.download_button[0].mime == "application/zip"
    assert at.download_button[0].file_name.startswith("Session_13_")
    assert at.download_button[0].file_name.endswith(".zip")
    assert isinstance(at.session_state.output_zip_buffer, io.BytesIO)

    # Check that open was called for each file expected to be written
    m_open = mock_external_dependencies
    expected_writes = [
        "sector_playbook.json",
        "validation_checklist.md",
        "monitoring_kpis.json",
        "incident_triggers.json",
        "config_snapshot.json",
        "executive_summary.md",
    ]
    mock_open_calls = [call.args[0] for call in m_open.call_args_list if call.args[1] == 'w']
    for filename in expected_writes:
        assert any(filename in call_path for call_path in mock_open_calls)

def test_export_panel_page_warning_if_components_not_generated():
    """
    Tests that "Export Panel" shows a warning if playbook components are not generated.
    """
    at = AppTest.from_file("app.py").run()
    at.button[0].click().run() # Load data, but don't generate components
    at.selectbox[0].set_value("Export Panel").run()
    assert at.warning[0].value == "Please go to 'Sector & Use-Case Wizard' and generate playbook components first."
    assert at.button[0].disabled is True # "Generate All Final Artifacts" button should be disabled

def test_persona_selection_changes_content():
    """
    Tests that changing the persona updates the displayed text on the "Sector & Use-Case Wizard" page.
    """
    at = AppTest.from_file("app.py").run()
    
    # Change persona using the sidebar selectbox (selectbox[1])
    at.selectbox[1].set_value("Domain AI Lead").run()

    assert at.session_state.persona == "Domain AI Lead"
    # Verify that the displayed text reflecting the persona has changed
    assert "Domain" in at.markdown[1].value # Check for 'Domain' in the paragraph describing Evelyn Reed's role
    assert "Evelyn Reed" not in at.markdown[1].value # The initial specific name part of the sentence
    assert "Domain AI Lead" in at.markdown[1].value # The full persona string will also be mentioned
