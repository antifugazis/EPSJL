from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from modules.whatsapp_recipients_manager import recipients_manager

# Create blueprint
whatsapp_management_blueprint = Blueprint('whatsapp_management', __name__)

@whatsapp_management_blueprint.route('/whatsapp/recipients', methods=['GET'])
@login_required
def list_recipients():
    """Display the list of WhatsApp recipients"""
    recipients = recipients_manager.get_all_recipients()
    return render_template('whatsapp/recipients.html', recipients=recipients)

@whatsapp_management_blueprint.route('/whatsapp/recipients/add', methods=['GET', 'POST'])
@login_required
def add_recipient():
    """Add a new WhatsApp recipient"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        active = request.form.get('active') == 'on'
        
        if not name or not phone:
            flash('Name and phone number are required', 'danger')
            return redirect(url_for('whatsapp_management.add_recipient'))
        
        success = recipients_manager.add_recipient(name, phone, active)
        
        if success:
            flash('Recipient added successfully', 'success')
            return redirect(url_for('whatsapp_management.list_recipients'))
        else:
            flash('Failed to add recipient. Phone number may already exist.', 'danger')
            return redirect(url_for('whatsapp_management.add_recipient'))
    
    return render_template('whatsapp/add_recipient.html')

@whatsapp_management_blueprint.route('/whatsapp/recipients/edit/<phone>', methods=['GET', 'POST'])
@login_required
def edit_recipient(phone):
    """Edit an existing WhatsApp recipient"""
    # Get all recipients
    recipients = recipients_manager.get_all_recipients()
    
    # Find the recipient with the given phone number
    recipient = next((r for r in recipients if r.get('phone') == phone), None)
    
    if not recipient:
        flash('Recipient not found', 'danger')
        return redirect(url_for('whatsapp_management.list_recipients'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        new_phone = request.form.get('phone')
        active = request.form.get('active') == 'on'
        
        if not name or not new_phone:
            flash('Name and phone number are required', 'danger')
            return redirect(url_for('whatsapp_management.edit_recipient', phone=phone))
        
        success = recipients_manager.update_recipient(
            phone=phone,
            name=name,
            new_phone=new_phone,
            active=active
        )
        
        if success:
            flash('Recipient updated successfully', 'success')
            return redirect(url_for('whatsapp_management.list_recipients'))
        else:
            flash('Failed to update recipient', 'danger')
            return redirect(url_for('whatsapp_management.edit_recipient', phone=phone))
    
    return render_template('whatsapp/edit_recipient.html', recipient=recipient)

@whatsapp_management_blueprint.route('/whatsapp/recipients/delete/<phone>', methods=['POST'])
@login_required
def delete_recipient(phone):
    """Delete a WhatsApp recipient"""
    success = recipients_manager.delete_recipient(phone)
    
    if success:
        flash('Recipient deleted successfully', 'success')
    else:
        flash('Failed to delete recipient', 'danger')
    
    return redirect(url_for('whatsapp_management.list_recipients'))

# API endpoints for AJAX operations
@whatsapp_management_blueprint.route('/api/whatsapp/recipients', methods=['GET'])
@login_required
def api_list_recipients():
    """API endpoint to get all recipients"""
    recipients = recipients_manager.get_all_recipients()
    return jsonify({"recipients": recipients})

@whatsapp_management_blueprint.route('/api/whatsapp/recipients', methods=['POST'])
@login_required
def api_add_recipient():
    """API endpoint to add a recipient"""
    data = request.json
    
    if not data or not data.get('name') or not data.get('phone'):
        return jsonify({"success": False, "message": "Name and phone are required"}), 400
    
    success = recipients_manager.add_recipient(
        name=data.get('name'),
        phone=data.get('phone'),
        active=data.get('active', True)
    )
    
    if success:
        return jsonify({"success": True, "message": "Recipient added successfully"})
    else:
        return jsonify({"success": False, "message": "Failed to add recipient"}), 400

@whatsapp_management_blueprint.route('/api/whatsapp/recipients/<phone>', methods=['PUT'])
@login_required
def api_update_recipient(phone):
    """API endpoint to update a recipient"""
    data = request.json
    
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    success = recipients_manager.update_recipient(
        phone=phone,
        name=data.get('name'),
        new_phone=data.get('phone'),
        active=data.get('active')
    )
    
    if success:
        return jsonify({"success": True, "message": "Recipient updated successfully"})
    else:
        return jsonify({"success": False, "message": "Failed to update recipient"}), 400

@whatsapp_management_blueprint.route('/api/whatsapp/recipients/<phone>', methods=['DELETE'])
@login_required
def api_delete_recipient(phone):
    """API endpoint to delete a recipient"""
    success = recipients_manager.delete_recipient(phone)
    
    if success:
        return jsonify({"success": True, "message": "Recipient deleted successfully"})
    else:
        return jsonify({"success": False, "message": "Failed to delete recipient"}), 400
