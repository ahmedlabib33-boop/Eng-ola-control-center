from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from ola_360.core.config import Settings
from ola_360.core.config import _writable_db_path
from ola_360.core.security import hash_password, verify_password
from ola_360.repositories.app_repository import AppRepository
from ola_360.repositories.database import init_db
from ola_360.services.ai_service import AIService
from ola_360.services.auth_service import AuthService
from ola_360.services.brief_service import MorningBriefService
from ola_360.services.calendar_service import CalendarService
from ola_360.services.channel_service import ChannelService
from ola_360.services.digest_service import DigestService
from ola_360.services.escalation_service import EscalationService
from ola_360.services.export_service import ExportService
from ola_360.services.import_service import ImportService
from ola_360.services.notification_service import NotificationService
from ola_360.services.portfolio_service import PortfolioService
from ola_360.services.premium_service import PremiumService
from ola_360.services.query_service import NaturalQueryService
from ola_360.services.report_service import ReportService
from ola_360.services.speech_service import SpeechToTextService


@pytest.fixture()
def repo(tmp_path: Path) -> AppRepository:
    db_path = tmp_path / "ola_360_test.db"
    init_db(db_path)
    return AppRepository(db_path)


def test_password_hashing_round_trip() -> None:
    encoded = hash_password("Ola360!")
    assert "Ola360!" not in encoded
    assert verify_password("Ola360!", encoded)
    assert not verify_password("wrong", encoded)


def test_authentication(repo: AppRepository) -> None:
    auth = AuthService(repo, Settings(db_path=repo.db_path))
    user = auth.authenticate("ola@samco.local", "Ola360!")
    assert user.name == "Eng. Ola"
    with pytest.raises(ValueError):
        auth.authenticate("ola@samco.local", "bad")


def test_db_path_falls_back_when_configured_parent_is_unwritable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    blocked_file = tmp_path / "not_a_directory"
    blocked_file.write_text("blocked", encoding="utf-8")
    fallback = tmp_path / "runtime"
    monkeypatch.setattr("tempfile.gettempdir", lambda: str(fallback))

    resolved = _writable_db_path(blocked_file / "data" / "ola_360.db")

    assert resolved == fallback / "ola360_runtime" / "data" / "ola_360_runtime.db"
    assert resolved.parent.exists()


def test_morning_brief_uses_stored_data(repo: AppRepository) -> None:
    brief = MorningBriefService(repo).build()
    assert brief["critical_count"] >= 1
    assert "stored" not in brief["summary"].lower() or brief["critical_count"] == 0


def test_warning_creation_and_filter(repo: AppRepository) -> None:
    warning_id = repo.create_warning(
        {
            "title": "Procurement issue requires intervention",
            "category": "Procurement",
            "sector": "Tunnels",
            "project": "Configured PMO Project",
            "severity": "Intervention",
            "trend": "New",
            "owner": "Procurement Lead",
            "due_date": "2099-01-01",
        }
    )
    filtered = repo.warnings(sector="Tunnels", severity="Intervention")
    assert len(filtered) == 1
    assert filtered[0].owner == "Procurement Lead"
    repo.update_warning_core(warning_id, "Updated procurement issue", "PMO Lead", "2099-01-02")
    updated = [item for item in repo.warnings() if item.id == warning_id][0]
    assert updated.title == "Updated procurement issue"
    assert updated.owner == "PMO Lead"


def test_meeting_commitment_decision_workflows(repo: AppRepository) -> None:
    meeting_id = repo.create_meeting("Sector review", "Sector review", "2099-01-01")
    commitment_id = repo.create_commitment("Submit evidence", "Project Manager", "2099-01-02")
    decision_id = repo.create_decision("Approve instruction", "Configured PMO Project", "2099-01-03")
    assert meeting_id > 0
    assert commitment_id > 0
    assert decision_id > 0
    repo.update_commitment_status(commitment_id, "Completed", 100)
    repo.update_decision_status(decision_id, "Approved")
    repo.update_commitment_core(commitment_id, "Submit final evidence", "PMO Lead", "2099-01-04", "Medium")
    repo.update_decision_core(decision_id, "Approve final instruction", "Configured PMO Project", "2099-01-05")
    assert any(item.id == commitment_id and item.status == "Completed" for item in repo.commitments())
    assert any(item.id == decision_id and item.status == "Approved" for item in repo.decisions())
    assert any(item.id == commitment_id and item.title == "Submit final evidence" for item in repo.commitments())
    assert any(item.id == decision_id and item.title == "Approve final instruction" for item in repo.decisions())


def test_meeting_intelligence_generates_management_outputs(repo: AppRepository) -> None:
    ai = AIService(repo)
    transcript = (
        "Decision approved for Building B01 recovery plan.\n"
        "Action: submit revised recovery plan because the delay is critical."
    )
    result = ai.extract_meeting_intelligence(
        transcript,
        "Buildings sector review",
    )
    assert result["verbatim_transcript"] == transcript
    assert result["discussion_summary"]
    assert result["discussion_summary"].startswith("- ")
    assert "Transcript captured:" in result["extraction_quality"]
    assert "Decision approved" in result["decision"]
    assert "submit revised recovery plan" in result["action_required"]
    assert result["responsible_person"] == "Project Manager"
    assert result["priority"] == "Critical"
    assert "Meeting:" in result["meeting_minutes"]
    assert "Subject:" in result["follow_up_email_draft"]
    assert "Next" not in result["action_register"]


def test_speech_service_requires_real_provider_configuration(tmp_path: Path) -> None:
    audio = tmp_path / "meeting.wav"
    audio.write_bytes(b"not-a-real-wave-but-existing-file")
    service = SpeechToTextService()
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        service.transcribe_file(str(audio))


def test_meeting_intelligence_extracts_review_labels(repo: AppRepository) -> None:
    ai = AIService(repo)
    result = ai.extract_meeting_intelligence(
        "\n".join(
            [
                "Discussion summary: Buildings delay reviewed with procurement impact.",
                "Decision: Submit revised recovery plan by 6 July.",
                "Action required: Prepare recovery plan and evidence pack.",
                "Responsible person: Project Controls Lead",
                "Due date: 2026-07-06",
                "Priority: Critical",
                "Related project: Building B01",
                "Related warning: Milestone delay warning",
                "Supporting attachment: uploads/b01-delay-note.pdf",
            ]
        ),
        "Buildings sector review",
    )

    assert result["discussion_summary"] == "Buildings delay reviewed with procurement impact."
    assert result["decision"] == "Submit revised recovery plan by 6 July."
    assert result["action_required"] == "Prepare recovery plan and evidence pack."
    assert result["responsible_person"] == "Project Controls Lead"
    assert result["due_date"] == "2026-07-06"
    assert result["priority"] == "Critical"
    assert result["related_project"] == "Building B01"
    assert result["related_warning"] == "Milestone delay warning"
    assert result["supporting_attachment"] == "uploads/b01-delay-note.pdf"
    assert "Meeting: Buildings sector review" in result["meeting_minutes"]
    assert "Project Controls Lead" in result["action_register"]
    assert "Submit revised recovery plan" in result["decision_register"]
    assert "Subject: Follow-up actions" in result["follow_up_email_draft"]
    assert "Review closure evidence" in result["next_meeting_agenda"]
    assert result["overdue_action_list"]


def test_ai_fallback_excludes_private_data(repo: AppRepository) -> None:
    ai = AIService(repo)
    response = ai.answer("What requires my attention today?")
    assert "Private My Day records are excluded" in response["answer"]
    assert response["sources"] == "Local SQLite records"


def test_natural_language_query_uses_stored_data(repo: AppRepository) -> None:
    answer = NaturalQueryService(repo).answer("Show me all overdue actions related to Configured PMO Project")
    assert "Submit recovery-plan evidence" in answer
    assert "Project Manager" in answer


def test_portfolio_rollup_predictive_and_escalation(repo: AppRepository) -> None:
    repo.create_project_update(
        {
            "project": "Risk Trend Project",
            "sector": "Buildings",
            "update_date": "2099-01-01",
            "progress": "50",
            "summary": "Baseline",
            "issues": "Procurement risk",
        }
    )
    repo.create_project_update(
        {
            "project": "Risk Trend Project",
            "sector": "Buildings",
            "update_date": "2099-01-02",
            "progress": "50",
            "summary": "Flat progress",
            "issues": "Procurement delay risk remains",
        }
    )
    rollup = PortfolioService(repo).rollup()
    flags = PortfolioService(repo).predictive_flags()
    escalations = EscalationService(repo).overdue_escalations()
    assert rollup["red_projects"] >= 1
    assert any(item["project"] == "Risk Trend Project" for item in flags)
    assert any("suggested_nudge" in item for item in escalations)


def test_calendar_channel_digest_decision_audit_and_voice_capture(repo: AppRepository, tmp_path: Path) -> None:
    ics = """BEGIN:VCALENDAR
BEGIN:VEVENT
UID:meeting-1
SUMMARY:Executive calendar review
DTSTART:20990101T090000Z
DTEND:20990101T100000Z
END:VEVENT
END:VCALENDAR
"""
    calendar_result = CalendarService(repo).import_ics(ics, "unit-test")
    digest = DigestService(repo, tmp_path / "exports").build_digest("weekly")
    channel_result = ChannelService(repo).send_email("leader@example.com", "Subject", "Body")
    capture_id = repo.create_voice_capture("private_note", "voice.wav", "Call project director", "My Day")
    audit = repo.decision_audit()

    assert calendar_result["imported"] == 1
    assert any(item.title == "Executive calendar review" for item in repo.meetings())
    assert digest["markdown"].exists()
    assert digest["pdf"].exists()
    assert channel_result["status"] == "draft"
    assert capture_id > 0
    assert audit


def test_private_data_isolation(repo: AppRepository) -> None:
    task_id = repo.create_private_task("Private family call", "Family", "2099-01-01")
    repo.update_private_task_status(task_id, "Closed")
    repo.update_private_task_core(task_id, "Private family follow-up", "Call", "2099-01-02")
    context = repo.ai_records_context(include_private=False)
    assert "private_tasks" not in context
    assert "personal_events" not in context
    assert "private_notes" not in context
    assert "wellbeing_checkins" not in context
    private_context = repo.ai_records_context(include_private=True)
    assert any(item["title"] == "Private family follow-up" for item in private_context["private_tasks"])
    assert any(item.status == "Closed" and item.title == "Private family follow-up" for item in repo.private_tasks())


def test_import_validation(repo: AppRepository, tmp_path: Path) -> None:
    csv_path = tmp_path / "warnings.csv"
    csv_path.write_text("title,owner\nA,B\n", encoding="utf-8")
    preview = repo.import_csv_preview(csv_path)
    assert preview == [{"title": "A", "owner": "B"}]


def test_checked_in_templates_import(repo: AppRepository) -> None:
    importer = ImportService(repo)
    root = Path(__file__).resolve().parents[1]
    warning_result = importer.import_csv(str(root / "templates" / "warnings_template.csv"), "warnings")
    evidence_result = importer.import_csv(str(root / "templates" / "warning_evidence_template.csv"), "warning_evidence")
    project_result = importer.import_csv(str(root / "templates" / "projects_template.csv"), "projects")
    meeting_result = importer.import_csv(str(root / "templates" / "meetings_template.csv"), "meetings")
    attendee_result = importer.import_csv(str(root / "templates" / "attendees_template.csv"), "attendees")
    agenda_result = importer.import_csv(str(root / "templates" / "agenda_items_template.csv"), "agenda_items")
    commitment_result = importer.import_csv(str(root / "templates" / "commitments_template.csv"), "commitments")
    decision_result = importer.import_csv(str(root / "templates" / "decisions_template.csv"), "decisions")
    milestone_result = importer.import_csv(str(root / "templates" / "milestones_template.csv"), "milestones")
    update_result = importer.import_csv(str(root / "templates" / "project_updates_template.csv"), "project_updates")
    comment_result = importer.import_csv(str(root / "templates" / "comments_template.csv"), "comments")
    attachment_result = importer.import_csv(str(root / "templates" / "attachments_template.csv"), "attachments")
    private_result = importer.import_csv(str(root / "templates" / "personal_tasks_template.csv"), "personal_tasks")
    event_result = importer.import_csv(str(root / "templates" / "personal_events_template.csv"), "personal_events")
    note_result = importer.import_csv(str(root / "templates" / "private_notes_template.csv"), "private_notes")
    wellbeing_result = importer.import_csv(str(root / "templates" / "wellbeing_checkins_template.csv"), "wellbeing_checkins")
    assert warning_result == {"imported": 1, "errors": []}
    assert evidence_result == {"imported": 1, "errors": []}
    assert project_result == {"imported": 1, "errors": []}
    assert meeting_result == {"imported": 1, "errors": []}
    assert attendee_result == {"imported": 1, "errors": []}
    assert agenda_result == {"imported": 1, "errors": []}
    assert commitment_result == {"imported": 1, "errors": []}
    assert decision_result == {"imported": 1, "errors": []}
    assert milestone_result == {"imported": 1, "errors": []}
    assert update_result == {"imported": 1, "errors": []}
    assert comment_result == {"imported": 1, "errors": []}
    assert attachment_result == {"imported": 1, "errors": []}
    assert private_result == {"imported": 1, "errors": []}
    assert event_result == {"imported": 1, "errors": []}
    assert note_result == {"imported": 1, "errors": []}
    assert wellbeing_result == {"imported": 1, "errors": []}
    milestone = [item for item in repo.milestones() if item.title == "Submit revised recovery plan"][0]
    repo.update_milestone_status(milestone.id, "Completed")
    assert any(item.id == milestone.id and item.status == "Completed" for item in repo.milestones())


def test_delete_records(repo: AppRepository) -> None:
    warning_id = repo.create_warning(
        {
            "title": "Delete me",
            "category": "Risk",
            "sector": "Buildings",
            "project": "Configured PMO Project",
            "severity": "Watch",
            "trend": "New",
            "owner": "PMO",
            "due_date": "2099-01-01",
        }
    )
    commitment_id = repo.create_commitment("Temporary action", "PMO", "2099-01-01")
    decision_id = repo.create_decision("Temporary decision", "Configured PMO Project", "2099-01-01")
    task_id = repo.create_private_task("Temporary private task", "Priority", "2099-01-01")
    milestone_id = repo.create_milestone_from_data({"title": "Temporary milestone", "due_date": "2099-01-01"})
    project_id = repo.create_project_from_data({"name": "Temporary project master", "sector": "Buildings", "status": "Active"})
    update_id = repo.create_project_update(
        {
            "project": "Temporary project",
            "sector": "Buildings",
            "update_date": "2099-01-01",
            "summary": "Temporary update",
        }
    )
    comment_id = repo.create_comment_from_data({"entity_type": "project", "entity_id": project_id, "body": "Temporary comment"})
    attachment_id = repo.create_attachment_from_data({"entity_type": "project", "entity_id": project_id, "file_path": "uploads/temp.pdf"})
    evidence_id = repo.create_warning_evidence_from_data({"warning_id": warning_id, "evidence_text": "Temporary evidence"})
    attendee_id = repo.create_attendee_from_data({"meeting_id": 1, "name": "Temporary attendee"})
    agenda_id = repo.create_agenda_item_from_data({"meeting_id": 1, "title": "Temporary agenda item"})
    event_id = repo.create_personal_event("Temporary event", "2099-01-01", "Personal")
    note_id = repo.create_private_note("Temporary note", "Body")
    checkin_id = repo.create_wellbeing_checkin("2099-01-01", 1, 0, 4)
    repo.delete_record("warning", warning_id)
    repo.delete_record("commitment", commitment_id)
    repo.delete_record("decision", decision_id)
    repo.delete_record("private_task", task_id)
    repo.delete_record("milestone", milestone_id)
    repo.delete_record("comment", comment_id)
    repo.delete_record("attachment", attachment_id)
    repo.delete_record("warning_evidence", evidence_id)
    repo.delete_record("attendee", attendee_id)
    repo.delete_record("agenda_item", agenda_id)
    repo.delete_record("project_update", update_id)
    repo.delete_record("project", project_id)
    repo.delete_record("personal_event", event_id)
    repo.delete_record("private_note", note_id)
    repo.delete_record("wellbeing_checkin", checkin_id)
    assert all(item.id != warning_id for item in repo.warnings())
    assert all(item.id != commitment_id for item in repo.commitments())
    assert all(item.id != decision_id for item in repo.decisions())
    assert all(item.id != task_id for item in repo.private_tasks())
    assert all(item.id != milestone_id for item in repo.milestones())
    assert all(item.id != comment_id for item in repo.comments())
    assert all(item.id != attachment_id for item in repo.attachments())
    assert all(item.id != evidence_id for item in repo.warning_evidence())
    assert all(item.id != attendee_id for item in repo.attendees())
    assert all(item.id != agenda_id for item in repo.agenda_items())
    assert all(item.id != update_id for item in repo.project_updates())
    assert all(item.id != project_id for item in repo.projects())
    assert all(item.id != event_id for item in repo.personal_events())
    assert all(item.id != note_id for item in repo.private_notes())
    assert all(item.id != checkin_id for item in repo.wellbeing_checkins())


def test_private_events_notes_and_wellbeing(repo: AppRepository) -> None:
    event_id = repo.create_personal_event("Renew passport", "2099-03-01", "Document renewal")
    note_id = repo.create_private_note("Books to read", "Leadership and project controls")
    checkin_id = repo.create_wellbeing_checkin("2099-03-01", 1, 1, 2)

    private_context = repo.ai_records_context(include_private=True)
    assert any(item["id"] == event_id and item["title"] == "Renew passport" for item in private_context["personal_events"])
    assert any(item["id"] == note_id and item["title"] == "Books to read" for item in private_context["private_notes"])
    assert any(item["id"] == checkin_id and item["stress_level"] == 2 for item in private_context["wellbeing_checkins"])


def test_project_updates_and_stale_notification(repo: AppRepository) -> None:
    update_id = repo.create_project_update(
        {
            "project": "Fresh PMO Project",
            "sector": "Buildings",
            "update_date": "2099-01-01",
            "progress": "75",
            "summary": "Fresh update",
            "next_milestone": "Executive review",
            "issues": "None",
        }
    )

    assert any(item.id == update_id and item.progress == 75 for item in repo.project_updates())
    notifications = NotificationService(repo).build_notifications()
    assert any("Missing recent project update" in item for item in notifications)


def test_project_master_comments_and_attachments(repo: AppRepository) -> None:
    project_id = repo.create_project_from_data({"name": "Roads Package A", "sector": "Roads", "status": "Active"})
    comment_id = repo.create_comment_from_data({"entity_type": "project", "entity_id": project_id, "author": "Eng. Ola", "body": "Review traffic diversion evidence."})
    attachment_id = repo.create_attachment_from_data({"entity_type": "project", "entity_id": project_id, "file_name": "evidence.pdf", "file_path": "uploads/evidence.pdf"})
    context = repo.ai_records_context(include_private=False)

    assert any(item.id == project_id and item.sector == "Roads" for item in repo.projects())
    assert any(item.id == comment_id and "traffic diversion" in item.body for item in repo.comments())
    assert any(item.id == attachment_id and item.file_name == "evidence.pdf" for item in repo.attachments())
    assert any(item["name"] == "Roads Package A" for item in context["projects"])
    assert any(item["file_name"] == "evidence.pdf" for item in context["attachments"])


def test_reviewed_meeting_extraction_saves_registers(repo: AppRepository) -> None:
    ai = AIService(repo)
    extraction = ai.extract_meeting_intelligence(
        "Decision agreed to issue recovery instruction.\n"
        "Action: prepare action tracker before the urgent sector review.",
        "Sector review",
    )
    extraction["responsible_person"] = "Sector Lead"
    extraction["priority"] = "Critical"
    extraction["supporting_attachment"] = "uploads/recovery-note.pdf"
    saved = repo.save_reviewed_meeting_extraction("Sector review", "Sector review", "Transcript text", extraction)

    assert saved["meeting_id"] > 0
    assert any(item.id == saved["commitment_id"] and item.owner == "Sector Lead" and item.priority == "Critical" for item in repo.commitments())
    assert any(item.id == saved["decision_id"] and item.title == extraction["decision"] for item in repo.decisions())


def test_xlsx_import_and_exports(repo: AppRepository, tmp_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["title", "owner", "due_date", "project", "sector", "priority"])
    sheet.append(["Prepare executive note", "PMO Lead", "2099-02-01", "Configured PMO Project", "Buildings", "High"])
    xlsx_path = tmp_path / "commitments.xlsx"
    workbook.save(xlsx_path)

    importer = ImportService(repo)
    result = importer.import_file(str(xlsx_path), "commitments")
    assert result == {"imported": 1, "errors": []}
    assert any(item.title == "Prepare executive note" for item in repo.commitments())

    exporter = ExportService(repo, tmp_path / "exports")
    warnings_file = exporter.export("warnings")
    projects_file = exporter.export("projects")
    commitments_file = exporter.export("commitments")
    project_updates_file = exporter.export("project_updates")
    comments_file = exporter.export("comments")
    attachments_file = exporter.export("attachments")
    evidence_file = exporter.export("warning_evidence")
    meetings_file = exporter.export("meetings")
    attendees_file = exporter.export("attendees")
    agenda_file = exporter.export("agenda_items")
    private_file = exporter.export("private_tasks")
    events_file = exporter.export("personal_events")
    notes_file = exporter.export("private_notes")
    wellbeing_file = exporter.export("wellbeing_checkins")
    assert warnings_file.exists()
    assert projects_file.exists()
    assert commitments_file.exists()
    assert project_updates_file.exists()
    assert comments_file.exists()
    assert attachments_file.exists()
    assert evidence_file.exists()
    assert meetings_file.exists()
    assert attendees_file.exists()
    assert agenda_file.exists()
    assert private_file.exists()
    assert events_file.exists()
    assert notes_file.exists()
    assert wellbeing_file.exists()
    assert "title" in commitments_file.read_text(encoding="utf-8-sig")


def test_executive_report_uses_pmo_data_and_excludes_private_data(repo: AppRepository, tmp_path: Path) -> None:
    repo.create_private_task("Private family travel", "Family", "2099-01-01")
    repo.create_warning(
        {
            "title": "Critical procurement delay",
            "category": "Procurement",
            "sector": "Buildings",
            "project": "Building B01",
            "severity": "Critical",
            "trend": "Deteriorating",
            "owner": "Procurement Lead",
            "due_date": "2099-01-01",
        }
    )
    repo.create_commitment("Submit procurement recovery evidence", "Procurement Lead", "2000-01-01", "Building B01", "Critical")
    repo.create_decision("Approve procurement escalation", "Building B01", "2099-01-02")
    repo.create_meeting("Buildings sector review", "Sector review", "2099-01-03")
    repo.create_project_update(
        {
            "project": "Building B01",
            "sector": "Buildings",
            "update_date": "2099-01-01",
            "progress": "62",
            "summary": "Procurement recovery is under review.",
        }
    )

    output = ReportService(repo, tmp_path / "exports").build_executive_report()
    body = output.read_text(encoding="utf-8")

    assert output.exists()
    assert "# OLA 360 Executive PMO Report" in body
    assert "Critical procurement delay" in body
    assert "Submit procurement recovery evidence" in body
    assert "Approve procurement escalation" in body
    assert "Buildings sector review" in body
    assert "Procurement recovery is under review." in body
    assert "Private family travel" not in body
    assert "My Day private tasks" in body


def test_mobile_premium_service_surfaces_command_features(repo: AppRepository) -> None:
    repo.create_warning(
        {
            "title": "Director intervention required",
            "category": "Schedule",
            "sector": "Buildings",
            "project": "Building B01",
            "severity": "Critical",
            "trend": "Deteriorating",
            "owner": "PMO Lead",
            "due_date": "1999-01-01",
        }
    )
    repo.create_commitment("Close urgent recovery action", "PMO Lead", "2000-01-01", "Building B01", "Critical")
    repo.create_decision("Approve revised sequence", "Building B01", "2099-01-02")

    premium = PremiumService(repo)
    focus = premium.executive_focus()
    intervention = premium.intervention_items()
    templates = premium.template_catalog()
    shutdown = premium.shutdown_review()
    timeline = premium.recent_timeline()

    assert any(item["title"] == "Director intervention required" for item in focus)
    assert any(item["kind"] == "Commitment" for item in intervention)
    assert any(item["name"] == "warnings_template.csv" for item in templates)
    assert shutdown["tomorrow_priority"]
    assert timeline
