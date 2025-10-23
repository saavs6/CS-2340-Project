from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages as django_messages
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q, Max
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Conversation, Message
from .forms import NewConversationForm, MessageForm, ConversationSearchForm
from accounts.models import UserProfile

@login_required
def conversation_list(request):
    """Display list of conversations for the logged-in user"""
    
    # Get user's conversations
    if request.user.userprofile.user_type == 'recruiter':
        conversations = Conversation.objects.filter(recruiter=request.user)
    else:
        conversations = Conversation.objects.filter(applicant=request.user)
    
    # Search functionality
    search_form = ConversationSearchForm(request.GET)
    if search_form.is_valid() and search_form.cleaned_data['search']:
        search_term = search_form.cleaned_data['search']
        conversations = conversations.filter(
            Q(subject__icontains=search_term) |
            Q(recruiter__username__icontains=search_term) |
            Q(applicant__username__icontains=search_term)
        )
    
    # Order by last message time
    conversations = conversations.order_by('-last_message_at', '-created_at')
    
    # Add additional data to each conversation for template
    conversations_with_data = []
    for conversation in conversations:
        conversation_data = {
            'conversation': conversation,
            'other_participant': conversation.get_other_participant(request.user),
            'unread_count': conversation.get_unread_count(request.user),
            'latest_message': conversation.get_latest_message(),
        }
        conversations_with_data.append(conversation_data)
    
    # Pagination
    paginator = Paginator(conversations_with_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'user_type': request.user.userprofile.user_type,
    }
    
    return render(request, 'messages/conversation_list.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """Display conversation details and messages"""
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Security check: user must be a participant
    if request.user not in [conversation.recruiter, conversation.applicant]:
        raise Http404("Conversation not found")
    
    # Mark messages as read
    conversation.mark_as_read(request.user)
    
    # Get messages
    message_list = conversation.messages.all()
    
    # Pagination for messages
    paginator = Paginator(message_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Message form
    message_form = MessageForm()
    
    context = {
        'conversation': conversation,
        'page_obj': page_obj,
        'message_form': message_form,
        'other_participant': conversation.get_other_participant(request.user),
        'user_type': request.user.userprofile.user_type,
    }
    
    return render(request, 'messages/conversation_detail.html', context)

@login_required
def new_conversation(request):
    """Start a new conversation"""
    
    if request.method == 'POST':
        form = NewConversationForm(request.POST, user=request.user)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            
            # Create conversation with proper recruiter/applicant assignment
            if request.user.userprofile.user_type == 'recruiter':
                conversation = Conversation.objects.create(
                    recruiter=request.user,
                    applicant=recipient,
                    subject=form.cleaned_data['subject']
                )
            else:
                conversation = Conversation.objects.create(
                    recruiter=recipient,
                    applicant=request.user,
                    subject=form.cleaned_data['subject']
                )
            
            django_messages.success(request, 'Conversation started successfully!')
            return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    else:
        form = NewConversationForm(user=request.user)
    
    context = {
        'form': form,
        'user_type': request.user.userprofile.user_type,
    }
    
    return render(request, 'messages/new_conversation.html', context)

@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """Send a new message in a conversation"""
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Security check: user must be a participant
    if request.user not in [conversation.recruiter, conversation.applicant]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    form = MessageForm(request.POST)
    if form.is_valid():
        # Determine recipient
        recipient = conversation.get_other_participant(request.user)
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            recipient=recipient,
            content=form.cleaned_data['content']
        )
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({'error': 'Invalid form data'}, status=400)

@login_required
def start_conversation_with_user(request, user_id):
    """Start a conversation with a specific user (from their profile)"""
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Security check: can only message users of different type
    if not hasattr(target_user, 'userprofile'):
        raise Http404("User profile not found")
    
    if request.user.userprofile.user_type == target_user.userprofile.user_type:
        django_messages.error(request, "You can only message users of a different type.")
        return redirect('home:index')
    
    # Check if conversation already exists
    if request.user.userprofile.user_type == 'recruiter':
        existing_conversation = Conversation.objects.filter(
            recruiter=request.user,
            applicant=target_user
        ).first()
    else:
        existing_conversation = Conversation.objects.filter(
            recruiter=target_user,
            applicant=request.user
        ).first()
    
    if existing_conversation:
        return redirect('messaging:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    if request.user.userprofile.user_type == 'recruiter':
        conversation = Conversation.objects.create(
            recruiter=request.user,
            applicant=target_user,
            subject=f"Conversation with {target_user.username}"
        )
    else:
        conversation = Conversation.objects.create(
            recruiter=target_user,
            applicant=request.user,
            subject=f"Conversation with {target_user.username}"
        )
    
    django_messages.success(request, f'Started conversation with {target_user.username}')
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
def get_unread_count(request):
    """API endpoint to get unread message count"""
    
    if request.user.userprofile.user_type == 'recruiter':
        conversations = Conversation.objects.filter(recruiter=request.user)
    else:
        conversations = Conversation.objects.filter(applicant=request.user)
    
    total_unread = 0
    for conversation in conversations:
        total_unread += conversation.get_unread_count(request.user)
    
    return JsonResponse({'unread_count': total_unread})

@login_required
def mark_conversation_read(request, conversation_id):
    """Mark all messages in a conversation as read"""
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Security check: user must be a participant
    if request.user not in [conversation.recruiter, conversation.applicant]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    conversation.mark_as_read(request.user)
    
    return JsonResponse({'success': True})