import markdown
from django.utils.safestring import mark_safe

def markdown_to_html(markdown_text: str) -> str:
    """
    Convert Markdown text to safe HTML for rendering in Django templates.
    """
    if not markdown_text:
        return ""
    
    html = markdown.markdown(
        markdown_text,
        extensions=["extra", "toc", "fenced_code", "tables"]
    )
    return mark_safe(html)  # prevent auto-escaping in templates
