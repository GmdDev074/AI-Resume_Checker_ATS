"""PDF report generation using ReportLab."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from resume_analyzer.config.settings import Settings, get_settings
from resume_analyzer.models.report_model import ReportPayload
from resume_analyzer.utils.file_utils import ensure_dir
from resume_analyzer.utils.logger import get_logger

logger = get_logger(__name__)


class PDFReportGenerator:
    """Generate professional PDF analysis reports."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize report generator.

        Args:
            settings: Application settings.
        """
        self._settings = settings or get_settings()

    def generate(self, payload: ReportPayload, output_path: Optional[Path] = None) -> Path:
        """
        Create PDF report file.

        Args:
            payload: Report data bundle.
            output_path: Optional custom path.

        Returns:
            Path to generated PDF.
        """
        ensure_dir(self._settings.reports_dir)
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = payload.candidate_name.replace(" ", "_")[:30]
            output_path = self._settings.reports_dir / f"report_{safe_name}_{timestamp}.pdf"

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1a365d"),
            spaceAfter=12,
        )
        story = [
            Paragraph(payload.report_title, title_style),
            Paragraph(f"Generated: {payload.generated_at.strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
            Spacer(1, 0.2 * inch),
        ]
        story.extend(self._candidate_section(payload, styles))
        story.extend(self._scores_section(payload, styles))
        story.extend(self._skills_section(payload, styles))
        story.extend(self._recommendations_section(payload, styles))

        doc.build(story)
        logger.info("Report saved to %s", output_path)
        return Path(output_path)

    def _candidate_section(self, payload: ReportPayload, styles) -> list:
        """Build candidate info paragraphs."""
        c = payload.candidate
        lines = [
            f"<b>Name:</b> {c.name or 'N/A'}",
            f"<b>Email:</b> {c.email or 'N/A'}",
            f"<b>Phone:</b> {c.phone or 'N/A'}",
            f"<b>Experience:</b> {payload.resume.total_experience_years} years",
            f"<b>Skills Count:</b> {payload.resume.skills_count}",
        ]
        return [Paragraph("<br/>".join(lines), styles["Normal"]), Spacer(1, 0.25 * inch)]

    def _scores_section(self, payload: ReportPayload, styles) -> list:
        """Build score table."""
        data = [
            ["Metric", "Score"],
            ["ATS Score", f"{payload.analysis.ats.ats_score} ({payload.analysis.ats.grade})"],
            ["Job Match Score", f"{payload.analysis.match.match_score}%"],
            ["Semantic Similarity", f"{payload.analysis.match.semantic_similarity}%"],
        ]
        table = Table(data, colWidths=[3 * inch, 2.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b6cb0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ebf8ff")]),
                ]
            )
        )
        return [Paragraph("<b>Scores</b>", styles["Heading2"]), table, Spacer(1, 0.25 * inch)]

    def _skills_section(self, payload: ReportPayload, styles) -> list:
        """Build skill analysis section."""
        matched = ", ".join(payload.analysis.match.matched_skills[:15]) or "None"
        missing = ", ".join(payload.analysis.match.missing_skills[:15]) or "None"
        text = (
            f"<b>Matched Skills:</b> {matched}<br/><br/>"
            f"<b>Missing Skills:</b> {missing}"
        )
        return [Paragraph("<b>Skill Analysis</b>", styles["Heading2"]), Paragraph(text, styles["Normal"]), Spacer(1, 0.25 * inch)]

    def _recommendations_section(self, payload: ReportPayload, styles) -> list:
        """Build recommendations list."""
        items = payload.analysis.recommendations or ["No recommendations."]
        bullets = "<br/>".join(f"• {item}" for item in items[:12])
        return [
            Paragraph("<b>Recommendations</b>", styles["Heading2"]),
            Paragraph(bullets, styles["Normal"]),
        ]
