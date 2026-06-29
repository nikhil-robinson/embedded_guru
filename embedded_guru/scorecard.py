"""
EmbeddedGuru assessment scorecard — generates a PDF certificate from a JSON results file.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from fpdf import FPDF

# ── brand ──────────────────────────────────────────────────────────────────────
BRAND       = "EmbeddedGuru"
AUTHOR      = "Nikhil Robinson"
GITHUB      = "github.com/nikhil-robinson/embedded_guru"
WATERMARK   = f"Powered by {BRAND}  ·  Created by {AUTHOR}  ·  {GITHUB}"

# ── colours (R, G, B) ──────────────────────────────────────────────────────────
C_BG        = (10,  15,  30)    # near-black header
C_ACCENT    = (0,  180, 216)    # electric cyan
C_GOLD      = (251, 191,  36)   # grade badge
C_WHITE     = (255, 255, 255)
C_LIGHT     = (240, 242, 247)   # alternating row bg
C_DARK_TEXT = (20,  20,  40)
C_MID       = (100, 110, 130)
C_BAR_BG    = (220, 225, 235)
C_BAR_LOW   = (239,  68,  68)   # red   <50
C_BAR_MID   = (251, 146,  60)   # amber 50-69
C_BAR_OK    = (34,  197,  94)   # green >=70

# ── grade thresholds ───────────────────────────────────────────────────────────
GRADES = [
    (90, "Principal Engineer"),
    (80, "Expert"),
    (70, "Senior Engineer"),
    (55, "Engineer"),
    (40, "Practitioner"),
    ( 0, "Novice"),
]

CATEGORY_LABELS = {
    "core_firmware":       "Core Firmware Fundamentals",
    "protocols":           "Protocol Knowledge",
    "safety_reliability":  "Safety & Reliability",
    "domain_expertise":    "Domain Expertise",
    "debugging":           "Debugging & Problem Solving",
}

WEIGHTS = {
    "core_firmware":       0.20,
    "protocols":           0.25,
    "safety_reliability":  0.20,
    "domain_expertise":    0.25,
    "debugging":           0.10,
}


def _grade(score: float) -> str:
    for threshold, label in GRADES:
        if score >= threshold:
            return label
    return "Novice"


def _bar_colour(score: float):
    if score >= 70:
        return C_BAR_OK
    if score >= 50:
        return C_BAR_MID
    return C_BAR_LOW


class ScorecardPDF(FPDF):
    def __init__(self, data: dict):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.data = data
        self.set_auto_page_break(auto=False)
        self.add_page()

    # ── header band ────────────────────────────────────────────────────────────
    def _draw_header(self):
        d = self.data
        # dark bg
        self.set_fill_color(*C_BG)
        self.rect(0, 0, 210, 52, "F")

        # accent stripe
        self.set_fill_color(*C_ACCENT)
        self.rect(0, 48, 210, 4, "F")

        # brand name
        self.set_text_color(*C_ACCENT)
        self.set_font("Helvetica", "B", 22)
        self.set_xy(12, 8)
        self.cell(0, 10, BRAND, ln=True)

        # subtitle
        self.set_text_color(*C_WHITE)
        self.set_font("Helvetica", "", 11)
        self.set_xy(14, 20)
        self.cell(0, 6, "Firmware Engineering Assessment Certificate -- embeddedguru")

        # student name
        self.set_font("Helvetica", "B", 16)
        self.set_xy(14, 30)
        self.cell(0, 8, d.get("name", "—"))

        # meta: domain | level | date
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*C_ACCENT)
        self.set_xy(14, 40)
        issued = d.get("date", datetime.today().strftime("%Y-%m-%d"))
        meta = f"Domain: {d.get('domain','—')}   ·   Level: {d.get('level','—')}   ·   Issued: {issued}"
        self.cell(0, 5, meta)

    # ── grade badge (top-right) ─────────────────────────────────────────────────
    def _draw_grade_badge(self, overall: float):
        grade = _grade(overall)
        # outer circle simulation — filled rounded rect
        bx, by, bw, bh = 148, 5, 52, 40
        self.set_fill_color(*C_GOLD)
        self.rect(bx, by, bw, bh, "F")

        self.set_text_color(*C_BG)
        self.set_font("Helvetica", "B", 22)
        self.set_xy(bx, by + 4)
        self.cell(bw, 10, f"{overall:.0f}", align="C")

        self.set_font("Helvetica", "B", 7)
        self.set_xy(bx, by + 15)
        self.cell(bw, 5, "/ 100", align="C")

        self.set_font("Helvetica", "B", 7)
        self.set_xy(bx, by + 22)
        # wrap long grade names
        lines = grade.split()
        if len(lines) > 1:
            self.cell(bw, 4, lines[0].upper(), align="C", ln=True)
            self.set_x(bx)
            self.cell(bw, 4, " ".join(lines[1:]).upper(), align="C")
        else:
            self.cell(bw, 5, grade.upper(), align="C")

    # ── scores section ─────────────────────────────────────────────────────────
    def _draw_scores(self, scores: Dict[str, float]):
        y = 62
        self.set_text_color(*C_DARK_TEXT)
        self.set_font("Helvetica", "B", 11)
        self.set_xy(12, y)
        self.cell(0, 7, "Category Scores")
        y += 10

        bar_x   = 14
        bar_w   = 130
        bar_h   = 6
        row_h   = 14
        label_w = 68

        for i, (key, label) in enumerate(CATEGORY_LABELS.items()):
            score = scores.get(key, 0)
            weight_pct = int(WEIGHTS[key] * 100)

            # alternating row bg
            if i % 2 == 0:
                self.set_fill_color(*C_LIGHT)
                self.rect(bar_x - 2, y - 2, 184, row_h, "F")

            # label
            self.set_text_color(*C_DARK_TEXT)
            self.set_font("Helvetica", "", 9)
            self.set_xy(bar_x, y)
            self.cell(label_w, 5, label)

            # weight tag
            self.set_text_color(*C_MID)
            self.set_font("Helvetica", "", 7)
            self.set_xy(bar_x + label_w - 2, y + 0.5)
            self.cell(12, 4, f"{weight_pct}%", align="R")

            # bar background
            bary = y + 6
            self.set_fill_color(*C_BAR_BG)
            self.rect(bar_x, bary, bar_w, bar_h, "F")

            # bar fill
            fill_w = bar_w * score / 100
            self.set_fill_color(*_bar_colour(score))
            self.rect(bar_x, bary, fill_w, bar_h, "F")

            # score label
            self.set_text_color(*C_DARK_TEXT)
            self.set_font("Helvetica", "B", 9)
            self.set_xy(bar_x + bar_w + 4, bary - 1)
            self.cell(20, bar_h + 2, f"{score:.0f} / 100")

            y += row_h

        return y

    # ── overall + notes ────────────────────────────────────────────────────────
    def _draw_overall(self, overall: float, notes: str, y: float):
        y += 6
        # divider
        self.set_draw_color(*C_ACCENT)
        self.set_line_width(0.5)
        self.line(14, y, 196, y)
        y += 6

        self.set_text_color(*C_DARK_TEXT)
        self.set_font("Helvetica", "B", 13)
        self.set_xy(14, y)
        self.cell(80, 7, f"Overall Score:  {overall:.1f} / 100")

        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*C_ACCENT)
        self.set_xy(100, y)
        self.cell(0, 7, f"Grade:  {_grade(overall)}")

        y += 12
        if notes:
            self.set_text_color(*C_MID)
            self.set_font("Helvetica", "I", 9)
            self.set_xy(14, y)
            self.multi_cell(180, 5, f"Mentor note: {notes}")
            y += 12

        return y

    # ── footer watermark ───────────────────────────────────────────────────────
    def _draw_footer(self):
        # bottom accent band
        self.set_fill_color(*C_BG)
        self.rect(0, 272, 210, 25, "F")
        self.set_fill_color(*C_ACCENT)
        self.rect(0, 272, 210, 1.5, "F")

        self.set_text_color(*C_MID)
        self.set_font("Helvetica", "", 7.5)
        self.set_xy(0, 278)
        self.cell(210, 5, WATERMARK, align="C")

        self.set_text_color(*C_ACCENT)
        self.set_font("Helvetica", "B", 7.5)
        self.set_xy(0, 284)
        self.cell(210, 5, "Share on LinkedIn  |  #EmbeddedGuru  |  #FirmwareEngineering", align="C")

    # ── linkedin tip box ───────────────────────────────────────────────────────
    def _draw_share_tip(self, y: float, overall: float):
        y = max(y, 210)
        self.set_fill_color(*C_BG)
        self.rect(14, y, 182, 22, "F")
        self.set_fill_color(*C_ACCENT)
        self.rect(14, y, 3, 22, "F")

        self.set_text_color(*C_WHITE)
        self.set_font("Helvetica", "B", 9)
        self.set_xy(20, y + 3)
        self.cell(0, 5, "Share your certificate")

        self.set_font("Helvetica", "", 8)
        self.set_text_color(180, 200, 220)
        self.set_xy(20, y + 9)
        self.cell(0, 5, 'Post this PDF on LinkedIn with the caption:')
        self.set_xy(20, y + 14)
        self.cell(0, 5, f'"Just passed the EmbeddedGuru assessment - {_grade(overall)} level  #EmbeddedGuru"')

    # ── render all ─────────────────────────────────────────────────────────────
    def render(self) -> None:
        d       = self.data
        scores  = d.get("scores", {})
        overall = d.get("overall", sum(
            scores.get(k, 0) * w for k, w in WEIGHTS.items()
        ))

        self._draw_header()
        self._draw_grade_badge(overall)
        y = self._draw_scores(scores)
        y = self._draw_overall(overall, d.get("notes", ""), y)
        self._draw_share_tip(y, overall)
        self._draw_footer()


# ── public API ─────────────────────────────────────────────────────────────────

def generate(assessment_json: Path, out_dir: Path | None = None) -> Path:
    """Generate a scorecard PDF from an assessment JSON file. Returns the PDF path."""
    assessment_json = Path(assessment_json)
    if not assessment_json.exists():
        raise FileNotFoundError(f"Assessment file not found: {assessment_json}")

    with open(assessment_json, encoding="utf-8") as f:
        data = json.load(f)

    # auto-compute overall if not present
    if "overall" not in data:
        scores = data.get("scores", {})
        data["overall"] = round(sum(scores.get(k, 0) * w for k, w in WEIGHTS.items()), 1)

    if "grade" not in data:
        data["grade"] = _grade(data["overall"])

    out_dir = Path(out_dir) if out_dir else assessment_json.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    date_str = data.get("date", datetime.today().strftime("%Y-%m-%d"))
    name_slug = data.get("name", "student").lower().replace(" ", "_")
    out_path  = out_dir / f"scorecard_{name_slug}_{date_str}.pdf"

    pdf = ScorecardPDF(data)
    pdf.render()
    pdf.output(str(out_path))

    return out_path
