"""
PDF generation utilities for ReelifyAI.

Requires fpdf2 >= 2.7.0 (install via `pip install fpdf2`).
The old fpdf 1.7.2 is NOT compatible with this module.
"""
from fpdf import FPDF
from typing import List


def _safe(text: str) -> str:
    """Encode text to Latin-1, replacing unsupported characters with '?'."""
    if not text:
        return ""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_repurpose_pdf(result: dict) -> bytes:
    """
    Build a formatted PDF from a /repurpose API response.

    Args:
        result: dict with keys 'summary', 'tweet_thread' (list), 'blog_intro'

    Returns:
        PDF content as bytes, ready for st.download_button.
    """
    summary: str = result.get("summary", "")
    tweets: List[str] = result.get("tweet_thread", [])
    blog: str = result.get("blog_intro", "")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Header ────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", style="B", size=20)
    pdf.cell(0, 12, "ReelifyAI - Content Package", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(108, 99, 255)
    pdf.set_line_width(0.5)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)

    # ── Summary ───────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, _safe(summary))
    pdf.ln(8)

    # ── Tweet Thread ──────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 8, "Tweet Thread", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    for i, tweet in enumerate(tweets, 1):
        pdf.set_font("Helvetica", style="B", size=9)
        pdf.cell(0, 6, f"Tweet {i} of {len(tweets)}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, _safe(tweet))
        pdf.ln(3)
    pdf.ln(5)

    # ── Blog Introduction ─────────────────────────────────────────────────────
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 8, "Blog Introduction", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    for para in blog.split("\n"):
        para = para.strip()
        if para:
            pdf.multi_cell(0, 6, _safe(para))
            pdf.ln(3)

    return bytes(pdf.output())
