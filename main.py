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

    ⚠️ Return the result **strictly as JSON** with the following format:

    {{
    "title": "Your generated title here (max 10 words)",
    "subtitle": "Your generated subtitle here (max 20 words)",
    "bullets": [
        "First key takeaway",
        "Second key takeaway",
        "Third key takeaway"
    ],
    "link": "https://example.com/source-or-infographic"
    }}

    Make sure each part is tailored to what would be relevant and useful for someone in that audience.

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

def generate_pdf(title, subtitle, bullets, output_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Title: {title}\n\nSubtitle: {subtitle}\n\nKey Points:\n" + "\n".join(f"- {b}" for b in bullets))
    pdf.output(output_path)

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

    output_pdf = f"summary_for_{target_audience.replace(' ', '_')}.pdf"
    generate_pdf(title, subtitle, bullets, output_pdf)

    print(f"✅ Summary PDF generated: {output_pdf}")