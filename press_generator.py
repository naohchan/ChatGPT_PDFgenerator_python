import fitz  # PyMuPDF
import json
from fpdf import FPDF
from dotenv import load_dotenv
import os
import openai
from openai import OpenAI

file_path = "SEED2GROW_example.pdf"

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 1. Extract text from PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return " ".join([page.get_text() for page in doc])

# 2. Generate press release from GPT
def generate_press_release_with_gpt(text, target_audience, api_key,retries=3):
    prompt = f"""

You are a skilled communications professional. Write two **different versions** of a press release about the following research paper, tailored for a {target_audience} audience.

Both versions must follow **strictly the JSON format**, with these fields:

{{
  "headline": "Short and impactful title",
  "subheadline": "Optional, one line of additional context",
  "dateline": "City, Country — Date",
  "lead_paragraph": "Concise opening paragraph with key info",
  "body_paragraphs": [
    "Body paragraph 1",
    "Body paragraph 2"
  ],
  "quote": "Optional quote from a project leader or expert",
  "boilerplate": "About the organization",
  "contact_info": "Name — Email — Phone"
}}

🎯 Version A: Write it with a **professional, formal, ethical and neutral tone** appropriate for official communication to {target_audience}.
🎨 Version B: Write it with a more **imaginative, warm, engaging and creative tone**, while still appropriate and respectful for {target_audience}.

Return the two versions in a single JSON object with two keys: `"option_a"` and `"option_b"`.  
Do not include any text outside of the JSON.
All fields must be included in both versions; if a field has no content, set it as an empty string.

Use the following text as the source material:
{text[:12000]}

Focus on clarity, journalistic style, and adherence to the structure above.
"""

    client = OpenAI(api_key=api_key)

    for attempt in range(1, retries + 1):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1500
        )

        raw_output = response.choices[0].message.content

        try:
            json_start = raw_output.find('{')
            json_end = raw_output.rfind('}') + 1
            json_str = raw_output[json_start:json_end]
            press_release = json.loads(json_str)
            return press_release
        except json.JSONDecodeError:
            print(f"⚠️ Attempt {attempt}: Failed to parse JSON. Retrying…")
            print("Raw output:")
            print(raw_output)
    print("❌ Failed to parse press release JSON after multiple attempts.")
    return None

# 3. Parse GPT output into title, subtitle, bullets
def parse_output(output_text):
    lines = output_text.strip().split("\n")
    title = lines[0].replace("Title:", "").strip()
    subtitle = lines[1].replace("Subtitle:", "").strip()
    bullets = [line.lstrip("-•* ").strip() for line in lines[2:] if line.strip()]
    return title, subtitle, bullets

# 4. Generate PDF from summary
class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font_path = "fonts/"
        self.add_font('DejaVu', '', font_path + 'DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', font_path + 'DejaVuSans-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', font_path + 'DejaVuSans-Oblique.ttf', uni=True)

    def header(self):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, 'AI Summary', ln=True, align='C')



def generate_press_release_pdf(
        headline, subheadline, dateline, lead_paragraph, 
        body_paragraphs, quote, boilerplate, contact_info, output_path):
    
    pdf = PDF()
    pdf.add_page()


    #upload the font .tts file
    font_path = "fonts/"

    #Header
    pdf.set_font("DejaVu", 'B', 12)
    pdf.cell(0, 10, 'FOR IMMEDIATE RELEASE', ln=True, align='C')
    pdf.ln(5)

    # Headline
    pdf.set_font("DejaVu", 'B', 16)
    pdf.multi_cell(0, 10, headline)

    # Subheadline
    if subheadline:
        pdf.set_font("DejaVu", 'I', 12)
        pdf.multi_cell(0, 10, subheadline)
    pdf.ln(5)

    # Dateline
    pdf.set_font("DejaVu", '', 12)
    pdf.multi_cell(0, 10, dateline)
    pdf.ln(5)

    # Lead Paragraph
    pdf.multi_cell(0, 10, lead_paragraph)
    pdf.ln(5)

    # Body
    for para in body_paragraphs:
        pdf.multi_cell(0, 10, para)
        pdf.ln(2)

    # Quote
    if quote:
        pdf.set_font("DejaVu", 'I', 12)
        pdf.multi_cell(0, 10, f'"{quote}"')
        pdf.ln(5)

    # Boilerplate
    pdf.set_font("DejaVu", '', 12)
    pdf.multi_cell(0, 10, boilerplate)
    pdf.ln(5)

    # Contact Info
    pdf.set_font("DejaVu", 'B', 12)
    pdf.multi_cell(0, 10, f'Contact: {contact_info}')
    
    pdf.output(output_path)
    print(f"✅ Press Release PDF generated: {output_path}")

# === RUNNING THE WHOLE FLOW ===
if __name__ == "__main__":
    file_path = "SEED2GROW_example.pdf"  # Replace with your PDF

#Select Audience
# Choose the target audience (e.g., policymakers, media, industry, academics,
# general public).
# Choose Summary Style
#Select a tone/style (e.g., professional, science communication).
# Select Output Format
#For now, the focus is on text-based formats only.

#Target Audience: Media Content Creator

#########################################    
    target_audience = "Policy Maker"
    #target_audience = "Media Content Creator"
#########################################

    extracted_text = extract_text_from_pdf(file_path)

    press_release = generate_press_release_with_gpt(extracted_text, target_audience, api_key)

    if press_release:
        for option, data in press_release.items():
            output_press_pdf = f"press_release_for_{target_audience.replace(' ', '_')}_{option.upper()}.pdf"

            generate_press_release_pdf(
                data["headline"],
                data["subheadline"],
                data["dateline"],
                data["lead_paragraph"],
                data["body_paragraphs"],
                data["quote"],
                data["boilerplate"],
                data["contact_info"],
                output_press_pdf
            )

