from django.template.loader import render_to_string
from django.conf import settings
from django.template import Template, Context

class NotificationTemplateEngine:
    """
    A simple template engine for rendering notification messages.
    """
    def __init__(self, template_dir='notifications_system/templates'):
        self.template_dir = template_dir

    def render(self, event_key: str, context: dict, channel: str = 'email') -> str:
        """
        Renders the appropriate template for the given event and channel.
        Example event_key: 'order_created', channel: 'email'
        """
        template_name = f"{self.template_dir}/{event_key.replace('.', '/')}.html"
        return render_to_string(template_name, context)

    def preview(self, event_key: str, channel: str = 'email', dummy_context: dict = None) -> str:
        """
        Previews the rendered template without sending it.
        """
        dummy_context = dummy_context or {"user_name": "John Doe", "order_id": 12345}
        return self.render(event_key, dummy_context, channel=channel)
    

    def render_template(self, template_data: dict, context: dict) -> str:
        """
        Renders a template with the provided context.
        """
        if isinstance(template_data, str):
            # If template_data is a string, treat it as a template name
            tmpl = Template(template_data)
            return tmpl.render(Context(context))
        elif isinstance(template_data, dict):
            # If template_data is a dictionary, it should contain 'template_name' and 'content'
            return {
                k: self.render_template(v, context) for k, v in template_data.items()
            }
        raise ValueError("Invalid template data format. Must be a string or a dictionary.")
