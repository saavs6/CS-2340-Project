import os
import django
from django.core.mail import send_mail
from django.conf import settings

# ----------------------------------------------------------------------
# 1. SETUP THE DJANGO ENVIRONMENT
#
# IMPORTANT: Replace 'your_project_name.settings' with the actual path
# to your Django settings module (e.g., 'myproject.settings').
# ----------------------------------------------------------------------
try:
    # Set the settings module for Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobapp.settings')

    # Initialize Django environment
    django.setup()

    print("Django environment configured successfully.")

except ImportError as e:
    print(f"Error configuring Django: {e}")
    print("Please ensure you are running this script from a virtual environment where Django is installed,")
    print("and that 'your_project_name.settings' is correctly set to your settings file path.")
    exit()

# ----------------------------------------------------------------------
# 2. EMAIL TEST PARAMETERS
# ----------------------------------------------------------------------

# The email address you want to send the test message TO
RECIPIENT_EMAIL = 'jxchen021@gmail.com'

# Subject and body of the test email
EMAIL_SUBJECT = "Django Email Test Success! 🚀"
EMAIL_MESSAGE = "If you receive this email, your SMTP configuration is working correctly!"

# Retrieve the sender address from Django settings (using the value from DEFAULT_FROM_EMAIL)
SENDER_EMAIL = settings.DEFAULT_FROM_EMAIL

# ----------------------------------------------------------------------
# 3. SEND THE EMAIL
# ----------------------------------------------------------------------

if RECIPIENT_EMAIL == 'test_recipient@example.com':
    print("\n--- WARNING: You must update the RECIPIENT_EMAIL variable in the script. ---")
    print(f"Test aborted. Current recipient: {RECIPIENT_EMAIL}")
    exit()


print(f"\nAttempting to send test email from: {SENDER_EMAIL} to: {RECIPIENT_EMAIL}")
print(f"Using EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

try:
    # send_mail(subject, message, from_email, recipient_list)
    send_mail(
        EMAIL_SUBJECT,
        EMAIL_MESSAGE,
        SENDER_EMAIL,
        [RECIPIENT_EMAIL],
        fail_silently=False, # We want to see errors if they occur
    )

    print("\n✅ Success! The email was sent.")
    print("Please check the inbox for the recipient address (and the spam folder!).")

except Exception as e:
    print("\n❌ Failure! The email was NOT sent.")
    print("A network or authentication error occurred. Please double-check your .env variables:")
    print(f"Error details: {e}")
