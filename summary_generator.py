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
def generate_summary_with_gpt(text, target_audience, api_key, retries=3):
    prompt = f"""
    You are an expert science communicator. Write two **different summaries** of the following research paper content, tailored for a {target_audience} audience.

    Both versions must follow **strictly the JSON format**, with these fields:

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

    🎯 Version A: Write it with a **professional, formal, ethical and neutral tone** appropriate for {target_audience}.
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
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )

        raw_output = response.choices[0].message.content

        try:
            json_start = raw_output.find('{')
            json_end = raw_output.rfind('}') + 1
            json_str = raw_output[json_start:json_end]
            summary = json.loads(json_str)
            return summary
        except json.JSONDecodeError:
            print(f"⚠️ Attempt {attempt}: Failed to parse JSON. Retrying…")
            print("Raw output:")
            print(raw_output)
    print("❌ Failed to parse summary JSON after multiple attempts.")
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
    
    gpt_output = generate_summary_with_gpt(extracted_text, target_audience, api_key)

    if gpt_output:
        for option, data in gpt_output.items():
            title = data["title"]
            subtitle = data["subtitle"]
            narrative = data["narrative"]
            bullets = data["bullets"]
            link = data["link"]

            output_pdf = f"summary_for_{target_audience.replace(' ', '_')}_{option.upper()}.pdf"
            generate_pdf(title, subtitle, narrative, bullets, link, output_pdf)
            print(f"✅ Summary PDF generated: {output_pdf}")
