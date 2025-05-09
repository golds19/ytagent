from fpdf import FPDF
import io
import os

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "ttf", "DejaVuSans.ttf")

def generate_pdf_bytes(summaries, insights):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Use Unicode-compatible font
    pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
    pdf.set_font("DejaVu", size=12)
    
    pdf.multi_cell(0, 10, "--- Summary ---")
    pdf.multi_cell(0, 10, summaries if isinstance(summaries, str) else "\n".join(summaries))


    pdf.ln(10)
    pdf.multi_cell(0, 10, "=== Final Insights ===")
    pdf.multi_cell(0, 10, insights)

    # ✅ Export to bytes using dest='S'
    pdf_bytes = pdf.output(dest='S').encode('latin1')  # Must be latin1 for PDF spec
    return pdf_bytes
