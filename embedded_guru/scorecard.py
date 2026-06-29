"""
EmbeddedGuru assessment certificate — generates a PNG from a JSON results file.
"""
from __future__ import annotations

import json
import textwrap
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── brand ──────────────────────────────────────────────────────────────────────
BRAND  = "EmbeddedGuru"
AUTHOR = "Nikhil Robinson"
GITHUB = "github.com/nikhil-robinson/embedded_guru"

# ── palette ────────────────────────────────────────────────────────────────────
C_LEFT_BG   = ( 10,  18,  42)   # deep navy
C_RIGHT_BG  = (255, 255, 255)   # white
C_ROW_ALT   = (238, 243, 250)   # alternating row tint
C_AMBER     = (245, 158,  11)   # gold accent
C_WHITE     = (255, 255, 255)
C_MUTED     = (148, 163, 184)   # muted on dark bg
C_INK       = ( 10,  18,  42)   # near-black text on white
C_MID       = ( 71,  85, 105)   # secondary text on white
C_SUBTLE    = (148, 163, 184)   # very muted on white
C_BAR_BG    = (209, 219, 233)   # bar track
C_GREEN     = ( 22, 163,  74)   # >= 70
C_ORANGE    = (234,  88,  12)   # 50-69
C_RED       = (220,  38,  38)   # < 50
C_DIVIDER   = (203, 213, 225)
C_SPLIT     = ( 20,  32,  70)   # vertical divider

# ── canvas ─────────────────────────────────────────────────────────────────────
W, H   = 1400, 900
SPLIT  =  440
PAD_L  =   42
PAD_R  =   52
PAD_RE =   44

# ── domain tables ──────────────────────────────────────────────────────────────
GRADES = [
    (90, "Principal Engineer"),
    (80, "Expert"),
    (70, "Senior Engineer"),
    (55, "Engineer"),
    (40, "Practitioner"),
    ( 0, "Novice"),
]

CATEGORY_LABELS = {
    "core_firmware":      "Core Firmware Fundamentals",
    "protocols":          "Protocol Knowledge",
    "safety_reliability": "Safety & Reliability",
    "domain_expertise":   "Domain Expertise",
    "debugging":          "Debugging & Problem Solving",
}

WEIGHTS = {
    "core_firmware":      0.20,
    "protocols":          0.25,
    "safety_reliability": 0.20,
    "domain_expertise":   0.25,
    "debugging":          0.10,
}

# ── fonts ──────────────────────────────────────────────────────────────────────
_FONTS = {
    "reg":  ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    "bold": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    "ital": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
}


def _load(style: str, size: int) -> ImageFont.FreeTypeFont:
    for path in _FONTS[style]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _grade(score: float) -> str:
    for threshold, label in GRADES:
        if score >= threshold:
            return label
    return "Novice"


def _bar_color(score: float):
    if score >= 70:
        return C_GREEN
    if score >= 50:
        return C_ORANGE
    return C_RED


# ── renderer ───────────────────────────────────────────────────────────────────

class CertificateRenderer:
    def __init__(self, data: dict):
        self.scores  = data.get("scores", {})
        self.overall = float(data.get("overall", sum(
            self.scores.get(k, 0) * w for k, w in WEIGHTS.items()
        )))
        self.grade   = _grade(self.overall)
        self.name    = data.get("name", "Student")
        self.domain  = data.get("domain", "-")
        self.level   = data.get("level", "-")
        self.date    = data.get("date", datetime.today().strftime("%Y-%m-%d"))
        self.notes   = data.get("notes", "")

        self.img = Image.new("RGB", (W, H), C_LEFT_BG)
        self.d   = ImageDraw.Draw(self.img)

    def _tw(self, text: str, font) -> int:
        return int(self.d.textlength(text, font=font))

    def _cx(self, text: str, font, x1: int, x2: int) -> int:
        return x1 + (x2 - x1 - self._tw(text, font)) // 2

    # ── LEFT PANEL ─────────────────────────────────────────────────────────────

    def _left(self):
        d  = self.d
        x  = PAD_L
        x2 = SPLIT - PAD_L

        # amber top stripe
        d.rectangle([0, 0, SPLIT, 7], fill=C_AMBER)

        # brand
        fb = _load("bold", 26)
        d.text((x, 26), BRAND, font=fb, fill=C_AMBER)

        # rule under brand
        d.rectangle([x, 63, x2, 65], fill=C_AMBER)

        # subtitle
        fn = _load("reg", 13)
        d.text((x, 72), "Firmware Engineering", font=fn, fill=C_MUTED)
        d.text((x, 92), "Assessment Certificate", font=fn, fill=C_MUTED)

        # certifies label
        fn10 = _load("reg", 10)
        d.text((x, 132), "THIS CERTIFIES THAT", font=fn10, fill=C_MUTED)

        # student name
        name_up = self.name.upper()
        nsz     = 38 if len(name_up) <= 14 else 30 if len(name_up) <= 20 else 22
        fb_name = _load("bold", nsz)
        d.text((x, 152), name_up, font=fb_name, fill=C_WHITE)

        # domain · level
        fn14 = _load("reg", 14)
        meta_y = 152 + nsz + 16
        d.text((x, meta_y), f"{self.domain}  |  {self.level}", font=fn14, fill=C_AMBER)
        fn12 = _load("reg", 12)
        d.text((x, meta_y + 22), self.date, font=fn12, fill=C_MUTED)

        # separator
        sep_y = meta_y + 58
        d.rectangle([x, sep_y, x2, sep_y + 1], fill=(30, 50, 100))

        # score — large
        fb_score = _load("bold", 110)
        score_str = f"{self.overall:.0f}"
        d.text((x, sep_y + 22), score_str, font=fb_score, fill=C_AMBER)
        sw = self._tw(score_str, fb_score)
        fn20 = _load("reg", 20)
        d.text((x + sw + 8, sep_y + 88), "/ 100", font=fn20, fill=C_MUTED)

        # grade badge
        badge_y = sep_y + 150
        d.rectangle([x, badge_y, x2, badge_y + 50], fill=C_AMBER)
        fb16 = _load("bold", 16)
        gu   = self.grade.upper()
        gx   = self._cx(gu, fb16, x, x2)
        d.text((gx, badge_y + 15), gu, font=fb16, fill=C_LEFT_BG)

        # bottom watermark
        d.text((x, H - 56), BRAND,             font=_load("bold", 11), fill=C_AMBER)
        d.text((x, H - 38), f"By {AUTHOR}",    font=_load("reg",  11), fill=C_MUTED)
        d.text((x, H - 20), GITHUB,             font=_load("reg",  10), fill=C_MUTED)

    # ── RIGHT PANEL ────────────────────────────────────────────────────────────

    def _right(self):
        d   = self.d
        rx  = SPLIT + PAD_R
        rx2 = W - PAD_RE

        # white background
        d.rectangle([SPLIT, 0, W, H], fill=C_RIGHT_BG)

        # amber top stripe
        d.rectangle([SPLIT, 0, W, 7], fill=C_AMBER)

        # ── "Category Scores" header ───────────────────────────────────────────
        cy = 28
        d.text((rx, cy), "Category Scores", font=_load("bold", 22), fill=C_INK)
        cy += 34
        d.rectangle([rx, cy, rx2, cy + 1], fill=C_DIVIDER)
        cy += 1   # cy is now at top of first row

        # ── rows ──────────────────────────────────────────────────────────────
        # divide the space: from cy to (H - footer - summary)
        FOOTER_H  = 70    # space reserved at bottom
        SUMMARY_H = 120   # overall + notes area
        row_area  = H - cy - FOOTER_H - SUMMARY_H
        ROW_H     = row_area // 5   # ~128px each

        BAR_H     = 20
        fn_lbl    = _load("bold", 18)
        fn_wt     = _load("reg",  14)
        fb_sc     = _load("bold", 17)

        for i, (key, label) in enumerate(CATEGORY_LABELS.items()):
            score      = float(self.scores.get(key, 0))
            weight_pct = int(WEIGHTS[key] * 100)
            row_y      = cy + i * ROW_H

            # alternating row background (full width)
            if i % 2 == 0:
                d.rectangle([SPLIT + 2, row_y, W, row_y + ROW_H], fill=C_ROW_ALT)

            # vertical centering within row
            content_h = 22 + 10 + BAR_H   # label + gap + bar
            top_pad   = (ROW_H - content_h) // 2
            ry        = row_y + top_pad

            # category label
            d.text((rx, ry), label, font=fn_lbl, fill=C_INK)

            # weight right-aligned on same line
            w_str = f"{weight_pct}%"
            d.text((rx2 - self._tw(w_str, fn_wt), ry + 3), w_str, font=fn_wt, fill=C_SUBTLE)

            ry += 28   # move to bar line

            # score label to right of bar
            score_str   = f"{int(score)} / 100"
            score_lbl_w = self._tw(score_str, fb_sc) + 16
            bar_end     = rx2 - score_lbl_w

            # bar track
            d.rectangle([rx, ry, bar_end, ry + BAR_H], fill=C_BAR_BG)

            # bar fill
            fill_px = max(0, int((bar_end - rx) * score / 100))
            if fill_px:
                d.rectangle([rx, ry, rx + fill_px, ry + BAR_H], fill=_bar_color(score))

            # score text
            d.text((bar_end + 10, ry + 1), score_str, font=fb_sc, fill=C_INK)

        # ── overall + grade ────────────────────────────────────────────────────
        sum_y = cy + 5 * ROW_H + 16
        d.rectangle([rx, sum_y, rx2, sum_y + 1], fill=C_DIVIDER)
        sum_y += 18

        fb20 = _load("bold", 20)
        overall_str = f"Overall Score:  {self.overall:.1f} / 100"
        d.text((rx, sum_y), overall_str, font=fb20, fill=C_INK)

        grade_str = f"Grade:  {self.grade}"
        gx = rx + self._tw(overall_str, fb20) + 32
        d.text((gx, sum_y), grade_str, font=fb20, fill=C_AMBER)
        sum_y += 42

        # ── mentor note ────────────────────────────────────────────────────────
        if self.notes:
            fi15    = _load("ital", 15)
            wrapped = textwrap.fill(self.notes, width=80)
            d.text((rx, sum_y), wrapped, font=fi15, fill=C_MID)

        # ── footer ─────────────────────────────────────────────────────────────
        foot_y = H - FOOTER_H + 8
        d.rectangle([rx, foot_y, rx2, foot_y + 1], fill=C_DIVIDER)
        foot_y += 10

        d.text((rx, foot_y),
               "Share on LinkedIn  |  #EmbeddedGuru  |  #FirmwareEngineering",
               font=_load("reg", 12), fill=C_AMBER)
        d.text((rx, foot_y + 22),
               f"Powered by {BRAND}  ·  {GITHUB}",
               font=_load("reg", 11), fill=C_SUBTLE)

    # ── vertical divider between panels ────────────────────────────────────────

    def _divider(self):
        self.d.rectangle([SPLIT, 0, SPLIT + 2, H], fill=C_SPLIT)

    # ── compose ────────────────────────────────────────────────────────────────

    def render(self) -> Image.Image:
        self._left()
        self._right()
        self._divider()
        return self.img


# ── public API ─────────────────────────────────────────────────────────────────

def generate(assessment_json: Path, out_dir: Path | None = None) -> Path:
    """Generate a scorecard PNG from an assessment JSON file. Returns the PNG path."""
    assessment_json = Path(assessment_json)
    if not assessment_json.exists():
        raise FileNotFoundError(f"Assessment file not found: {assessment_json}")

    with open(assessment_json, encoding="utf-8") as f:
        data = json.load(f)

    scores = data.get("scores", {})
    if "overall" not in data:
        data["overall"] = round(sum(scores.get(k, 0) * w for k, w in WEIGHTS.items()), 1)
    if "grade" not in data:
        data["grade"] = _grade(data["overall"])

    out_dir  = Path(out_dir) if out_dir else assessment_json.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    date_str  = data.get("date", datetime.today().strftime("%Y-%m-%d"))
    name_slug = data.get("name", "student").lower().replace(" ", "_")
    out_path  = out_dir / f"scorecard_{name_slug}_{date_str}.png"

    img = CertificateRenderer(data).render()
    img.save(str(out_path), "PNG", dpi=(150, 150))
    return out_path
