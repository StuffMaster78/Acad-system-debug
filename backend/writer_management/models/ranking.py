from django.db import models
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from django.contrib.auth import get_user_model
User = get_user_model()


class WriterAutoRanking(models.Model):
    """
    Auto-Promotion & Auto-Demotion based on writer performance.
    Admins can override.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="auto_ranking"
    )
    promoted = models.BooleanField(
        default=False,
        help_text="Has the writer been auto-promoted?"
    )
    demoted = models.BooleanField(
        default=False,
        help_text="Has the writer been auto-demoted?"
    )
    reason = models.TextField(
        help_text="Reason for auto-promotion/demotion."
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="ranking_reviews"
    )

    def __str__(self):
        return f"Auto-Ranking: {self.writer.user.username} (Promoted: {self.promoted}, Demoted: {self.demoted})"
    
class WriterRankingHistory(models.Model):
    """
    Tracks changes in writer rankings over time.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="ranking_history"
    )
    previous_level = models.CharField(
        max_length=100,
        help_text="Previous ranking level of the writer."
    )
    new_level = models.CharField(
        max_length=100,
        help_text="New ranking level of the writer."
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="ranking_changes"
    )

    def __str__(self):
        return f"Ranking Change: {self.writer.user.username} from {self.previous_level} to {self.new_level}"
    

    class Meta:
        verbose_name = "Writer Ranking History"
        verbose_name_plural = "Writer Ranking Histories"
        ordering = ['-changed_at']

class WriterRankingCriteria(models.Model):
    """
    Defines criteria for writer rankings.
    Admins can set thresholds for each level.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    level_name = models.CharField(
        max_length=100,
        help_text="Name of the ranking level."
    )
    min_orders_completed = models.PositiveIntegerField(
        default=0,
        help_text="Minimum orders completed to qualify for this level."
    )
    min_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        help_text="Minimum average rating to qualify for this level."
    )
    criteria_description = models.TextField(
        help_text="Description of the criteria for this ranking level."
    )

    def __str__(self):
        return f"Ranking Criteria: {self.level_name} (Min Orders: {self.min_orders_completed}, Min Rating: {self.min_rating})"
    
    class Meta:
        verbose_name = "Writer Ranking Criteria"
        verbose_name_plural = "Writer Ranking Criteria"
        ordering = ['level_name']

class WriterRanking(models.Model):
    """
    Tracks the current ranking of writers based on performance.
    Admins can manually adjust rankings.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="ranking"
    )
    level = models.CharField(
        max_length=100,
        help_text="Current ranking level of the writer."
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        help_text="Current average rating of the writer."
    )
    orders_completed = models.PositiveIntegerField(
        default=0,
        help_text="Total orders completed by the writer."
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ranking: {self.writer.user.username} - Level: {self.level} (Rating: {self.rating})"
    
    class Meta:
        verbose_name = "Writer Ranking"
        verbose_name_plural = "Writer Rankings"
        ordering = ['-last_updated']


class WriterRankingLog(models.Model):
    """
    Logs changes in writer rankings.
    Useful for auditing and tracking performance over time.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="ranking_logs"
    )
    previous_level = models.CharField(
        max_length=100,
        help_text="Previous ranking level of the writer."
    )
    new_level = models.CharField(
        max_length=100,
        help_text="New ranking level of the writer."
    )
    change_reason = models.TextField(
        help_text="Reason for the ranking change."
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="ranking_log_changes"
    )

    def __str__(self):
        return f"Ranking Log: {self.writer.user.username} from {self.previous_level} to {self.new_level}"
    
    class Meta:
        verbose_name = "Writer Ranking Log"
        verbose_name_plural = "Writer Ranking Logs"
        ordering = ['-changed_at']


class WriterRankingAdminReview(models.Model):
    """
    Admin reviews for writer rankings.
    Admins can provide feedback on ranking changes.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="ranking_admin_reviews"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="ranking_admin_reviews"
    )
    review_date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(
        blank=True, null=True,
        help_text="Admin comments on the ranking."
    )

    def __str__(self):
        return f"Admin Review: {self.writer.user.username} - {self.review_date}"
    
    class Meta:
        verbose_name = "Writer Ranking Admin Review"
        verbose_name_plural = "Writer Ranking Admin Reviews"
        ordering = ['-review_date']


class WriterRankingNotification(models.Model):
    """
    Notifications for writers about ranking changes.
    Sent when a writer's ranking is updated.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="ranking_notifications"
    )
    message = models.TextField(
        help_text="Notification message about the ranking change."
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification: {self.writer.user.username} - {self.sent_at} (Read: {self.read})"
    
    class Meta:
        verbose_name = "Writer Ranking Notification"
        verbose_name_plural = "Writer Ranking Notifications"
        ordering = ['-sent_at']

class WriterRankingCriteriaAdmin(models.Model):
    """
    Admin interface for managing writer ranking criteria.
    Allows admins to create, update, and delete ranking criteria.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    level_name = models.CharField(
        max_length=100,
        help_text="Name of the ranking level."
    )
    min_orders_completed = models.PositiveIntegerField(
        default=0,
        help_text="Minimum orders completed to qualify for this level."
    )
    min_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        help_text="Minimum average rating to qualify for this level."
    )
    criteria_description = models.TextField(
        help_text="Description of the criteria for this ranking level."
    )

    def __str__(self):
        return f"Admin Criteria: {self.level_name} (Min Orders: {self.min_orders_completed}, Min Rating: {self.min_rating})"
    
    class Meta:
        verbose_name = "Writer Ranking Criteria Admin"
        verbose_name_plural = "Writer Ranking Criteria Admins"
        ordering = ['level_name']