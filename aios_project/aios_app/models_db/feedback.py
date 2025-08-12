from django.db import models
from .user import User

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)  # Unique identifier for each feedback entry
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    content = models.TextField()  # The actual feedback message or comment
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('reviewed', 'Reviewed'),
            ('responded', 'Responded'),
        ],
        default='new'
    )
    response = models.TextField(blank=True, null=True)  # Admin’s response to the feedback (if any)
    created_at = models.DateTimeField(auto_now_add=True)  # Optional: track when feedback was submitted

    def __str__(self):
        return f"Feedback #{self.id} by {self.user.username}"

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']