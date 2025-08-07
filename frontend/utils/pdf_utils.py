from fpdf import FPDF
import io
import os

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Enable UTF-8 encoding
        self.add_font('DejaVu', '', os.path.join(os.path.dirname(__file__), 'fonts/ttf/DejaVuSans.ttf'), uni=True)
        self.add_font('DejaVu', 'B', os.path.join(os.path.dirname(__file__), 'fonts/ttf/DejaVuSans-Bold.ttf'), uni=True)

def generate_pdf_bytes(summaries, insights):
    """
    Generate PDF with Unicode support using DejaVu Sans font
    """
    try:
        # Create PDF object with Unicode support
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Set font to DejaVu (supports full Unicode)
        pdf.set_font('DejaVu', 'B', size=14)
        pdf.cell(0, 10, "Summary", ln=True)
        pdf.ln(5)
        
        # Add summary content
        pdf.set_font('DejaVu', '', size=12)
        content = summaries if isinstance(summaries, str) else "\n".join(summaries)
        # Split content into lines and add them one by one
        for line in content.split('\n'):
            pdf.multi_cell(0, 10, line.strip())
        pdf.ln(10)
        
        # Add insights section
        pdf.set_font('DejaVu', 'B', size=14)
        pdf.cell(0, 10, "Key Insights", ln=True)
        pdf.ln(5)
        
        pdf.set_font('DejaVu', '', size=12)
        # Handle insights content
        if insights:
            for line in insights.split('\n'):
                pdf.multi_cell(0, 10, line.strip())
        
        # Export to bytes with UTF-8 encoding
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        # If there's an encoding error, try to clean the text
        print(f"PDF Generation Error: {str(e)}")
        return generate_pdf_bytes_fallback(summaries, insights)

def generate_pdf_bytes_fallback(summaries, insights):
    """
    Fallback method with basic ASCII conversion
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Use built-in Arial font
    pdf.set_font('Arial', size=12)
    
    # Convert bullet points and special characters to basic ASCII
    def clean_text(text):
        if not text:
            return ""
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '•': '*',  # Replace bullet with asterisk
            '→': '->',  # Replace arrow
            '"': '"',  # Replace smart quotes
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '–': '-',
            '—': '-',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    pdf.cell(0, 10, "Summary", ln=True)
    content = clean_text(summaries if isinstance(summaries, str) else "\n".join(summaries))
    pdf.multi_cell(0, 10, content)
    
    pdf.ln(10)
    pdf.cell(0, 10, "Key Insights", ln=True)
    pdf.multi_cell(0, 10, clean_text(insights))
    
    return pdf.output(dest='S').encode('latin-1')