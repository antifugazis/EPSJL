"""
WhatsApp Notification Configuration

This file contains configuration settings for the WhatsApp notification system.
"""

# Wasender API Key
# Replace with your actual API key from wasenderapi.com
WASENDER_API_KEY = "2dabaeef98df0def0b1e6615e279523e64d31f43f340b309dc3f7196d0e42ad2"

# List of WhatsApp recipients to receive announcements
# Format: List of phone numbers with country code
# Example: ["+1234567890", "+1987654321"]
WHATSAPP_RECIPIENTS = [
    # Add your recipient phone numbers here
    "+50941877146",  # Example - replace with actual numbers
]

# Message template settings
# You can customize the message format here
MESSAGE_SETTINGS = {
    "include_expiration_date": True,
    "include_footer": True,
    "footer_text": "Pour plus d'informations, veuillez visiter notre site web."
}
