import json
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('whatsapp_recipients_manager')

class WhatsAppRecipientsManager:
    """
    Class to manage WhatsApp recipients with CRUD operations
    """
    def __init__(self, json_path=None):
        """
        Initialize the WhatsApp recipients manager
        
        Args:
            json_path (str, optional): Path to the JSON file containing recipients.
                                      If None, uses the default path.
        """
        if json_path is None:
            # Default path is in the config directory
            self.json_path = Path(__file__).parent.parent / 'config' / 'whatsapp_recipients.json'
        else:
            self.json_path = Path(json_path)
        
        # Ensure the file exists
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file exists, create it if it doesn't"""
        if not self.json_path.exists():
            # Create the directory if it doesn't exist
            self.json_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create an empty recipients file
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump({"recipients": []}, f, indent=2)
            
            logger.info(f"Created new recipients file at {self.json_path}")
    
    def get_all_recipients(self):
        """
        Get all recipients from the JSON file
        
        Returns:
            list: List of recipient dictionaries
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("recipients", [])
        except Exception as e:
            logger.error(f"Error reading recipients file: {str(e)}")
            return []
    
    def get_active_recipients(self):
        """
        Get only active recipients from the JSON file
        
        Returns:
            list: List of active recipient dictionaries
        """
        all_recipients = self.get_all_recipients()
        return [r for r in all_recipients if r.get("active", True)]
    
    def get_active_phone_numbers(self):
        """
        Get only the phone numbers of active recipients
        
        Returns:
            list: List of phone numbers
        """
        active_recipients = self.get_active_recipients()
        return [r.get("phone") for r in active_recipients if r.get("phone")]
    
    def add_recipient(self, name, phone, active=True):
        """
        Add a new recipient
        
        Args:
            name (str): Name of the recipient
            phone (str): Phone number of the recipient
            active (bool, optional): Whether the recipient is active. Defaults to True.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format the phone number if needed
            formatted_phone = self._format_phone_number(phone)
            
            # Get current recipients
            recipients = self.get_all_recipients()
            
            # Check if phone number already exists
            if any(r.get("phone") == formatted_phone for r in recipients):
                logger.warning(f"Phone number {formatted_phone} already exists")
                return False
            
            # Add new recipient
            recipients.append({
                "name": name,
                "phone": formatted_phone,
                "active": active
            })
            
            # Save back to file
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump({"recipients": recipients}, f, indent=2)
            
            logger.info(f"Added new recipient: {name} ({formatted_phone})")
            return True
        
        except Exception as e:
            logger.error(f"Error adding recipient: {str(e)}")
            return False
    
    def update_recipient(self, phone, name=None, new_phone=None, active=None):
        """
        Update an existing recipient
        
        Args:
            phone (str): Current phone number of the recipient to update
            name (str, optional): New name for the recipient
            new_phone (str, optional): New phone number for the recipient
            active (bool, optional): New active status for the recipient
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format the phone numbers
            formatted_phone = self._format_phone_number(phone)
            formatted_new_phone = self._format_phone_number(new_phone) if new_phone else None
            
            # Get current recipients
            recipients = self.get_all_recipients()
            
            # Find the recipient to update
            for i, recipient in enumerate(recipients):
                if recipient.get("phone") == formatted_phone:
                    # Update fields if provided
                    if name is not None:
                        recipients[i]["name"] = name
                    
                    if formatted_new_phone is not None:
                        recipients[i]["phone"] = formatted_new_phone
                    
                    if active is not None:
                        recipients[i]["active"] = active
                    
                    # Save back to file
                    with open(self.json_path, 'w', encoding='utf-8') as f:
                        json.dump({"recipients": recipients}, f, indent=2)
                    
                    logger.info(f"Updated recipient: {formatted_phone}")
                    return True
            
            logger.warning(f"Recipient with phone {formatted_phone} not found")
            return False
        
        except Exception as e:
            logger.error(f"Error updating recipient: {str(e)}")
            return False
    
    def delete_recipient(self, phone):
        """
        Delete a recipient
        
        Args:
            phone (str): Phone number of the recipient to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format the phone number
            formatted_phone = self._format_phone_number(phone)
            
            # Get current recipients
            recipients = self.get_all_recipients()
            
            # Filter out the recipient to delete
            new_recipients = [r for r in recipients if r.get("phone") != formatted_phone]
            
            # Check if any recipient was removed
            if len(new_recipients) == len(recipients):
                logger.warning(f"Recipient with phone {formatted_phone} not found")
                return False
            
            # Save back to file
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump({"recipients": new_recipients}, f, indent=2)
            
            logger.info(f"Deleted recipient: {formatted_phone}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting recipient: {str(e)}")
            return False
    
    def _format_phone_number(self, phone):
        """
        Ensure the phone number is properly formatted with country code
        
        Args:
            phone (str): Phone number which may or may not have country code
            
        Returns:
            str: Properly formatted phone number
        """
        if not phone:
            return None
            
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
recipients_manager = WhatsAppRecipientsManager()
