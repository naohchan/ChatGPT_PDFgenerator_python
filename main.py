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

# 2. Generate summary from GPT
def generate_summary_with_gpt(text, target_audience, api_key):
    prompt = f"""
    You are an expert science communicator. Summarise the following research paper content for a {target_audience} audience.

    Return the result **strictly as JSON** with the following fields:

    {{
    "title": "Short and engaging (max 10 words)",
    "subtitle": "Concise context (max 20 words)",
    "narrative": "A short paragraph (max 100 words) summarizing the key idea in a more natural, storytelling tone.",
    "bullets": [
        "Key takeaway 1",
        "Key takeaway 2",
        "Key takeaway 3"
    ],
    "link": "https://example.com/source-or-infographic"
    }}

    Only include information that is useful and relevant for someone in {target_audience}.

    Text:
    {text[:12000]}
    """


    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )

    raw_output = response.choices[0].message.content

    try:
        summary = json.loads(raw_output)
        return summary
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON. Raw output:")
        print(raw_output)
        return None

# 2. Generate press release from GPT
def generate_press_release_with_gpt(text, target_audience, api_key):
    prompt = f"""
You are a skilled communications professional. Write a press release about the following research paper, tailored for a {target_audience} audience.

Return the result **strictly as JSON**, with these fields:

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

Focus on clarity and journalistic tone.  
Use the following text as the source material:
{text[:12000]}
"""

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1000
    )

    raw_output = response.choices[0].message.content

    try:
        press_release = json.loads(raw_output)
        return press_release
    except json.JSONDecodeError:
        print("❌ Failed to parse press release JSON. Raw output:")
        print(raw_output)
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
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'AI Summary', ln=True, align='C')

def generate_pdf(title, subtitle, narrative, bullets, link, output_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"Title: {title}")
    pdf.multi_cell(0, 10, f"Subtitle: {subtitle}\n")
    
    pdf.set_font("Arial", 'I', 11)
    pdf.multi_cell(0, 10, f"{narrative}\n")

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Key Points:")
    for b in bullets:
        pdf.multi_cell(0, 10, f"- {b}")

    pdf.ln(10)
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Arial", 'U', 12)
    pdf.cell(0, 10, f"Source / Infographic: {link}", ln=True, link=link)

    pdf.output(output_path)




def generate_press_release_pdf(headline, subheadline, dateline, lead_paragraph, body_paragraphs, quote, boilerplate, contact_info, output_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'FOR IMMEDIATE RELEASE', ln=True, align='C')
    pdf.ln(5)

    # Headline
    pdf.set_font("Arial", 'B', 16)
    pdf.multi_cell(0, 10, headline)

    # Subheadline
    if subheadline:
        pdf.set_font("Arial", 'I', 12)
        pdf.multi_cell(0, 10, subheadline)
    pdf.ln(5)

    # Dateline
    pdf.set_font("Arial", '', 12)
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
        pdf.set_font("Arial", 'I', 12)
        pdf.multi_cell(0, 10, f'"{quote}"')
        pdf.ln(5)

    # Boilerplate
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, boilerplate)
    pdf.ln(5)

    # Contact Info
    pdf.set_font("Arial", 'B', 12)
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
    gpt_output = generate_summary_with_gpt(extracted_text, target_audience,api_key)
    title = gpt_output["title"]
    subtitle = gpt_output["subtitle"]
    bullets = gpt_output["bullets"]
    link = gpt_output["link"]
    narrative = gpt_output["narrative"]




    output_pdf = f"summary_for_{target_audience.replace(' ', '_')}.pdf"
    #generate_pdf(title, subtitle, bullets, output_pdf)
    generate_pdf(title, subtitle, narrative, bullets, link, output_pdf)

    print(f"✅ Summary PDF generated: {output_pdf}")

    press_release = generate_press_release_with_gpt(extracted_text, target_audience, api_key)

    if press_release:
        output_press_pdf = f"press_release_for_{target_audience.replace(' ', '_')}.pdf"

        generate_press_release_pdf(
            press_release["headline"],
            press_release["subheadline"],
            press_release["dateline"],
            press_release["lead_paragraph"],
            press_release["body_paragraphs"],
            press_release["quote"],
            press_release["boilerplate"],
            press_release["contact_info"],
            output_press_pdf
        )
