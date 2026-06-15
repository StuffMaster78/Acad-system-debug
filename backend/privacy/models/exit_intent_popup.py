from django.db import models


class ExitIntentPopupConfig(models.Model):
    TRIGGER_EXIT = "exit_intent"
    TRIGGER_DELAY = "delay"
    TRIGGER_SCROLL = "scroll_depth"
    TRIGGER_CHOICES = (
        (TRIGGER_EXIT, "Exit intent"),
        (TRIGGER_DELAY, "Time delay"),
        (TRIGGER_SCROLL, "Scroll depth"),
    )

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="exit_intent_popup_config",
    )
    is_enabled = models.BooleanField(default=False)
    trigger = models.CharField(max_length=32, choices=TRIGGER_CHOICES, default=TRIGGER_EXIT)
    title = models.CharField(max_length=140, default="Before you go")
    body = models.TextField(
        default="Need help choosing the right service? Get a quick quote and see your options before you leave."
    )
    primary_cta_label = models.CharField(max_length=80, default="Get a quick quote")
    primary_cta_url = models.CharField(max_length=255, default="/quote")
    secondary_cta_label = models.CharField(max_length=80, blank=True, default="Maybe later")
    image_url = models.URLField(blank=True, default="")
    show_on_paths = models.JSONField(
        default=list,
        blank=True,
        help_text="Path prefixes where the popup may show. Empty means all public pages.",
    )
    suppress_on_paths = models.JSONField(
        default=list,
        blank=True,
        help_text="Path prefixes where the popup must not show.",
    )
    delay_seconds = models.PositiveIntegerField(default=15)
    scroll_depth_percent = models.PositiveIntegerField(default=65)
    cooldown_hours = models.PositiveIntegerField(default=24)
    max_shows_per_session = models.PositiveIntegerField(default=1)
    requires_marketing_consent = models.BooleanField(
        default=False,
        help_text="When enabled, only show after the visitor accepts marketing cookies.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Exit intent popup config"
        verbose_name_plural = "Exit intent popup configs"

    def __str__(self):
        return f"{self.website}: {self.title}"
