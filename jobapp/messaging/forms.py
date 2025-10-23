from django import forms
from django.contrib.auth.models import User
from .models import Conversation, Message

class NewConversationForm(forms.ModelForm):
    """Form for starting a new conversation"""
    
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the person you want to message"
    )
    
    class Meta:
        model = Conversation
        fields = ['subject', 'recipient']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter conversation subject'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Set appropriate queryset based on user type
            if hasattr(user, 'userprofile'):
                if user.userprofile.user_type == 'recruiter':
                    # Recruiters can message applicants
                    self.fields['recipient'].queryset = User.objects.filter(
                        userprofile__user_type='applicant'
                    ).exclude(id=user.id)
                elif user.userprofile.user_type == 'applicant':
                    # Applicants can message recruiters
                    self.fields['recipient'].queryset = User.objects.filter(
                        userprofile__user_type='recruiter'
                    ).exclude(id=user.id)
    
    def clean(self):
        cleaned_data = super().clean()
        recipient = cleaned_data.get('recipient')
        user = getattr(self, 'user', None)
        
        if user and recipient:
            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(
                recruiter=user if user.userprofile.user_type == 'recruiter' else recipient,
                applicant=recipient if user.userprofile.user_type == 'recruiter' else user
            ).first()
            
            if existing_conversation:
                raise forms.ValidationError(
                    "A conversation with this person already exists. "
                    "Please use the existing conversation instead."
                )
        
        return cleaned_data

class MessageForm(forms.ModelForm):
    """Form for sending a new message"""
    
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your message here...',
                'required': True
            }),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError("Message content cannot be empty.")
        return content.strip()

class ConversationSearchForm(forms.Form):
    """Form for searching conversations"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search conversations...'
        })
    )
    
    def clean_search(self):
        search = self.cleaned_data.get('search')
        return search.strip() if search else ''


class EmailCandidateForm(forms.Form):
    """Form for emailing a candidate from a conversation"""

    to_email = forms.EmailField(
        disabled=True,
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Write your email message here...'})
    )

    def clean_body(self):
        body = self.cleaned_data.get('body', '')
        if not body.strip():
            raise forms.ValidationError("Email body cannot be empty.")
        return body.strip()
