from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils import timezone

class Conversation(models.Model):
    """Represents a conversation between a recruiter and an applicant"""
    
    # Participants
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recruiter_conversations')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applicant_conversations')
    
    # Optional: Link to a specific job application
    job_application = models.ForeignKey('jobs.JobApplication', on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    
    # Conversation metadata
    subject = models.CharField(max_length=200, help_text="Conversation subject")
    is_active = models.BooleanField(default=True, help_text="Whether the conversation is still active")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['recruiter', 'applicant', 'job_application']
        ordering = ['-last_message_at', '-created_at']
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
    
    def __str__(self):
        return f"{self.recruiter.username} ↔ {self.applicant.username} - {self.subject}"
    
    def get_other_participant(self, user):
        """Get the other participant in the conversation"""
        if user == self.recruiter:
            return self.applicant
        elif user == self.applicant:
            return self.recruiter
        return None
    
    def get_unread_count(self, user):
        """Get the number of unread messages for a user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()
    
    def mark_as_read(self, user):
        """Mark all messages as read for a user"""
        self.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)
    
    def get_latest_message(self):
        """Get the most recent message in the conversation"""
        return self.messages.order_by('-created_at').first()

class Message(models.Model):
    """Individual messages within a conversation"""
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    
    # Message content
    content = models.TextField(help_text="Message content")
    is_read = models.BooleanField(default=False, help_text="Whether the message has been read")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Message"
        verbose_name_plural = "Messages"
    
    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username}: {self.content[:50]}..."
    
    def mark_as_read(self):
        """Mark the message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def save(self, *args, **kwargs):
        """Override save to update conversation's last_message_at"""
        super().save(*args, **kwargs)
        # Update conversation's last_message_at
        self.conversation.last_message_at = self.created_at
        self.conversation.save(update_fields=['last_message_at'])

# Admin registration
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['recruiter', 'applicant', 'subject', 'is_active', 'created_at', 'last_message_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['recruiter__username', 'applicant__username', 'subject']
    readonly_fields = ['created_at', 'updated_at', 'last_message_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'conversation', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'content']
    readonly_fields = ['created_at', 'read_at']