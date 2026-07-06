from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ola_360.repositories.app_repository import AppRepository


class DigestService:
    def __init__(self, repo: AppRepository, export_dir: Path):
        self.repo = repo
        self.export_dir = export_dir

    def build_digest(self, period: str = "weekly") -> dict[str, Path]:
        self.export_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_path = self.export_dir / f"{period}_executive_digest_{stamp}.md"
        pdf_path = self.export_dir / f"{period}_executive_digest_{stamp}.pdf"
        body = self._markdown(period)
        md_path.write_text(body, encoding="utf-8")
        self._write_simple_pdf(pdf_path, body)
        return {"markdown": md_path, "pdf": pdf_path}

    def _markdown(self, period: str) -> str:
        warnings = [w for w in self.repo.warnings() if w.status != "Closed"]
        decisions = self.repo.decisions()
        commitments = self.repo.commitments()
        overdue = [c for c in commitments if c.status != "Completed"]
        decision_lines = [f"- {d.title} | {d.project} | {d.status} | Due: {d.due_date}" for d in decisions[:20]] or ["- No decisions stored."]
        warning_lines = [f"- {w.title} | {w.project} | {w.severity} | {w.trend}" for w in warnings[:20]] or ["- No open warnings stored."]
        commitment_lines = [f"- {c.title} | Owner: {c.owner} | Project: {c.project} | Due: {c.due_date}" for c in overdue[:20]] or ["- No open commitments stored."]
        lines = [
            f"# OLA 360 {period.title()} Executive Digest",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Leadership Snapshot",
            "",
            f"- Open warnings: {len(warnings)}",
            f"- Decisions recorded: {len(decisions)}",
            f"- Open commitments: {len(overdue)}",
            "",
            "## Decisions",
            "",
            *decision_lines,
            "",
            "## Risks Opened Or Still Active",
            "",
            *warning_lines,
            "",
            "## Overdue / Open Commitments",
            "",
            *commitment_lines,
            "",
            "## Privacy Boundary",
            "",
            "- Private My Day data is excluded.",
        ]
        return "\n".join(lines)

    def _write_simple_pdf(self, path: Path, text: str) -> None:
        safe_lines = [line[:100].replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") for line in text.splitlines()[:55]]
        content = ["BT", "/F1 10 Tf", "50 780 Td"]
        for index, line in enumerate(safe_lines):
            if index:
                content.append("0 -14 Td")
            content.append(f"({line}) Tj")
        content.append("ET")
        stream = "\n".join(content).encode("latin-1", errors="replace")
        objects = [
            b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
            b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
            b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
            b"5 0 obj << /Length " + str(len(stream)).encode() + b" >> stream\n" + stream + b"\nendstream endobj\n",
        ]
        out = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(len(out))
            out.extend(obj)
        xref_at = len(out)
        out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
        for offset in offsets[1:]:
            out.extend(f"{offset:010d} 00000 n \n".encode())
        out.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode())
        path.write_bytes(bytes(out))
