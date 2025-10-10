# notifications_system/services/render.py
from __future__ import annotations
from typing import Dict
from django.template import Template, Context
from notifications_system.models.notifications_template import NotificationTemplate

def render_template(tmpl: NotificationTemplate, payload: dict) -> Dict[str, str]:
    """Render subject/body using Django templates (very small, extend later)."""
    ctx = Context(payload or {})
    out: Dict[str, str] = {}
    if tmpl.subject:
        out["subject"] = Template(tmpl.subject).render(ctx)
    if tmpl.body_text:
        out["text"] = Template(tmpl.body_text).render(ctx)
    if tmpl.body_html:
        out["html"] = Template(tmpl.body_html).render(ctx)
    return out