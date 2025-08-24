import os
import logging
import requests
import json
import importlib.util
from pathlib import Path
from modules.whatsapp_recipients_manager import recipients_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('whatsapp_notifications')

class WhatsAppNotifier:
    """
    Class to handle sending WhatsApp notifications via Wasender API
    """
    def __init__(self):
        # Try to load config from the config file
        self.config = self._load_config()
        
        # Get API key from config or environment variable
        self.api_key = self.config.get('WASENDER_API_KEY') or os.getenv('WASENDER_API_KEY')
        
        # API endpoint
        self.api_url = "https://wasenderapi.com/api/send-message"
        
        if self.api_key:
            logger.info("WhatsApp notifier initialized successfully")
        else:
            logger.warning("WASENDER_API_KEY not found in config or environment variables")
    
    def _load_config(self):
        """Load configuration from the config file"""
        config = {}
        try:
            # Try to import the config file
            config_path = Path(__file__).parent.parent / 'config' / 'whatsapp_config.py'
            
            if config_path.exists():
                spec = importlib.util.spec_from_file_location("whatsapp_config", config_path)
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                
                # Extract configuration variables
                for key in dir(config_module):
                    if key.isupper():  # Only get uppercase variables (convention for constants)
                        config[key] = getattr(config_module, key)
                        
                logger.info(f"Loaded WhatsApp configuration from {config_path}")
            else:
                logger.warning(f"WhatsApp config file not found at {config_path}")
        except Exception as e:
            logger.error(f"Error loading WhatsApp config: {str(e)}")
            
        return config
    
    def is_configured(self):
        """Check if the notifier is properly configured"""
        return self.api_key is not None
    
    def send_announcement_notification(self, recipients, announcement):
        """
        Send WhatsApp notification about a new announcement to a list of recipients
        
        Args:
            recipients (list): List of phone numbers to send the notification to
            announcement (Annonce): The announcement object containing details to send
        
        Returns:
            dict: Results of sending attempts with phone numbers as keys and success status as values
        """
        if not self.is_configured():
            logger.error("WhatsApp notifier is not properly configured")
            return {"error": "WhatsApp notifier not configured"}
        
        results = {}
        
        # Format the message
        message = self._format_announcement_message(announcement)
        
        # Send to each recipient
        for phone in recipients:
            try:
                # Format the phone number if needed (ensure it has country code)
                formatted_phone = self._format_phone_number(phone)
                
                # Prepare the request
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "to": formatted_phone,
                    "text": message
                }
                
                # Send the message
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()  # Raise exception for HTTP errors
                response_data = response.json()
                
                # Log and store the result
                message_id = response_data.get('id', 'unknown')
                logger.info(f"Message sent to {formatted_phone}, ID: {message_id}")
                results[phone] = {
                    "success": True,
                    "message_id": message_id,
                    "response": response_data
                }
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API Error sending to {phone}: {str(e)}")
                results[phone] = {
                    "success": False,
                    "error": str(e)
                }
            except Exception as e:
                logger.error(f"Error sending to {phone}: {str(e)}")
                results[phone] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def _format_announcement_message(self, announcement):
        """Format the announcement into a WhatsApp message"""
        # Create a nicely formatted message with the announcement details
        message = f"*NOUVELLE ANNONCE*\n\n"
        message += f"*{announcement.titre}*\n\n"
        message += f"{announcement.contenu}\n\n"
        
        # Get message settings from config
        message_settings = self.config.get('MESSAGE_SETTINGS', {})
        
        # Add expiration date if available and configured
        if announcement.date_expiration and message_settings.get('include_expiration_date', True):
            message += f"Date d'expiration: {announcement.date_expiration.strftime('%d/%m/%Y')}\n\n"
        
        # Add a footer if configured
        if message_settings.get('include_footer', True):
            footer_text = message_settings.get('footer_text', "Pour plus d'informations, veuillez visiter notre site web.")
            message += footer_text
        
        return message
    
    def _format_phone_number(self, phone):
        """
        Ensure the phone number is properly formatted with country code
        
        Args:
            phone (str): Phone number which may or may not have country code
            
        Returns:
            str: Properly formatted phone number
        """
        # Remove any spaces, dashes, or parentheses
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # If the number doesn't start with a '+', add the default country code
        if not phone.startswith('+'):
            # Assuming default country code is +1 (US/Canada)
            # Change this to your default country code if different
            if clean_phone.startswith('1'):
                return f"+{clean_phone}"
            else:
                return f"+1{clean_phone}"
        
        return phone

# Create a singleton instance
whatsapp_notifier = WhatsAppNotifier()

def send_announcement_to_whatsapp(announcement, recipients=None):
    """
    Send an announcement to predefined WhatsApp recipients
    
    Args:
        announcement (Annonce): The announcement to send
        recipients (list, optional): List of phone numbers to send to. 
                                     If None, uses the predefined list from JSON file.
    
    Returns:
        dict: Results of the sending operation
    """
    # If no recipients provided, use the predefined list from JSON file
    if recipients is None:
        # Get active phone numbers from the recipients manager
        recipients = recipients_manager.get_active_phone_numbers()
        
        # If no recipients from JSON, fall back to config file
        if not recipients and hasattr(whatsapp_notifier, 'config') and 'WHATSAPP_RECIPIENTS' in whatsapp_notifier.config:
            recipients = whatsapp_notifier.config['WHATSAPP_RECIPIENTS']
        
        # If still no recipients, try environment variable
        if not recipients:
            recipients_str = os.getenv('WHATSAPP_RECIPIENTS', '')
            if recipients_str:
                recipients = [r.strip() for r in recipients_str.split(',')]
        
        # Log if no recipients found
        if not recipients:
            logger.warning("No WhatsApp recipients configured in any source")
    
    # Only send if we have recipients and the announcement is public
    if recipients and announcement.public:
        return whatsapp_notifier.send_announcement_notification(recipients, announcement)
    elif not announcement.public:
        logger.info("Announcement is not public, skipping WhatsApp notification")
        return {"status": "skipped", "reason": "announcement_not_public"}
    else:
        logger.info("No recipients configured, skipping WhatsApp notification")
        return {"status": "skipped", "reason": "no_recipients"}
