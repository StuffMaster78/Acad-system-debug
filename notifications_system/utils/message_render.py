from django.template.loader import render_to_string

def render_digest_email(digest):
    """
    Renders the digest into an HTML email using a template.
    """
    context = {
        "user": digest.user,
        "digest": digest,
        "items": digest.items.all() if hasattr(digest, "items") else [],  # Or however you're storing them
        "summary": digest.summary,  # Optional, if you store summaries
    }
    return render_to_string("emails/digest_email.html", context)
