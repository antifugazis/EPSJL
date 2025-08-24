"""
WhatsApp Notification Configuration

This file contains configuration settings for the WhatsApp notification system.
"""

# Wasender API Key
# Replace with your actual API key from wasenderapi.com
WASENDER_API_KEY = "2dabaeef98df0def0b1e6615e279523e64d31f43f340b309dc3f7196d0e42ad2"

# WhatsApp recipients are now managed in whatsapp_recipients.json
# This list is only used as a fallback if the JSON file is not available
# For CRUD operations, use the WhatsAppRecipientsManager class in modules/whatsapp_recipients_manager.py
WHATSAPP_RECIPIENTS = []  # Empty list as JSON file is the primary source

# Message template settings
# You can customize the message format here
MESSAGE_SETTINGS = {
    "include_expiration_date": True,
    "include_footer": True,
    "footer_text": "Pour plus d'informations, veuillez visiter notre site web."
}
