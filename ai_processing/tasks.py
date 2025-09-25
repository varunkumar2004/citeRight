from celery import shared_task
from papers.models import Paper, Tag
import PyPDF2
import requests
import json
# Import Django's settings to securely access the API key
from django.conf import settings

# The API URL is now built using the key from your settings file
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"

@shared_task
def generate_article_task(paper_id):
    """
    A Celery task to generate a full technical article and relevant tags from a PDF using the Gemini API.
    """
    try:
        paper = Paper.objects.get(id=paper_id)
    except Paper.DoesNotExist:
        return "Paper not found."

    try:
        full_text = ""
        with paper.pdf_file.open('rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                full_text += page.extract_text() or ""
        
        truncated_text = full_text[:12000]

        if not truncated_text.strip():
            paper.article_content = "Could not extract text from the PDF to generate an article."
            paper.save()
            return "No text extracted from PDF."

        prompt = f"""
        Analyze the following text from a research document. Your task is to:
        1. Generate a formal report consisting of simple text paragraphs. The report should cover an introduction, the key findings, and a conclusion. Ensure there is a new line after each paragraph. Do NOT use markdown headings, numbered lists, or bullet points.
        2. Identify 5 to 7 of the most relevant keywords or topics as tags.

        Return the result as a single JSON object with two keys: "report" and "tags".

        ---
        EXTRACTED TEXT:
        {truncated_text}
        ---
        """

        response_schema = {
            "type": "OBJECT",
            "properties": { "report": {"type": "STRING"}, "tags": { "type": "ARRAY", "items": {"type": "STRING"} } }
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": { "responseMimeType": "application/json", "responseSchema": response_schema }
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        response_data = result['candidates'][0]['content']['parts'][0]['text']

        paper.article_content = response_data.get("report", "AI failed to generate a report.")
        paper.save()

        generated_tags = response_data.get("tags", [])
        for tag_name in generated_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip().lower())
            paper.tags.add(tag)

        return f"Successfully generated article and tags for paper {paper.id}"

    except Exception as e:
        error_message = f"Failed to generate article: {str(e)}"
        paper.article_content = error_message
        paper.save()
        return error_message

