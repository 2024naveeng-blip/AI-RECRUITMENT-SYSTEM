import google.generativeai as genai
import PyPDF2

genai.configure(api_key="AIzaSyBlon1JamsOP3q8zxxUD8NYmUcPGccRTJU")

def extract_profile_text(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() for p in reader.pages])

def generate_technical_modules(profile, requirements, lang):
    engine = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Profile: {profile}\nRequirements: {requirements}\nGenerate 3 technical questions in {lang}. Max 15 words per question. Return only questions."
    response = engine.generate_content(prompt)
    return [q.strip() for q in response.text.strip().split('\n') if len(q) > 5][:3]

def analyze_performance_data(data_log, lang):
    engine = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Analyze these responses in {lang}: {data_log}. End strictly with 'OVERALL_SCORE: X/30'."
    response = engine.generate_content(prompt)
    return response.text