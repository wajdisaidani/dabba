from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Shipment, TrackingUpdate, Payment, Review, Message, ShipmentRequest, UserType, ShipmentStatus, ShipmentRequestStatus
from forms import LoginForm, RegisterForm, ShipmentForm, BookingForm, PaymentForm, ReviewForm, TrackingUpdateForm, MessageForm, ShipmentRequestForm
from utils import generate_mock_coordinates, generate_transaction_id
from datetime import datetime
import random
import json

@app.route('/')
def index():
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', today=today)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password_hash and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        elif user and not user.password_hash:
            flash(f'Questo account è collegato a {user.oauth_provider}. Usa il pulsante "{user.oauth_provider}" per accedere.', 'error')
        else:
            flash('Email o password non validi', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already registered', 'error')
            return render_template('register.html', form=form)
        
        # Generate new user ID
        import uuid
        user_id = str(uuid.uuid4())
        
        user = User(
            id=user_id,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! Welcome to dabba!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Sei stato disconnesso.', 'info')
    return redirect(url_for('index'))

# Login and registration routes already defined above

@app.route('/dashboard')
@login_required
def dashboard():
    # Get both sent and transported shipments for the user
    sent_shipments = current_user.sent_shipments.order_by(Shipment.created_at.desc()).all()
    transported_shipments = current_user.transported_shipments.order_by(Shipment.created_at.desc()).all()
    
    return render_template('dashboard.html', 
                         sent_shipments=sent_shipments,
                         transported_shipments=transported_shipments)

@app.route('/profile')
@login_required
def profile():
    # Calculate savings based on completed shipments
    completed_shipments = current_user.sent_shipments.filter_by(status=ShipmentStatus.DELIVERED).all()
    savings = sum(shipment.price for shipment in completed_shipments) if completed_shipments else 0
    
    return render_template('profile.html', savings=int(savings))

@app.route('/post-shipment', methods=['GET', 'POST'])
@login_required
def post_shipment():
    # Remove restriction - anyone can post shipments now
    form = ShipmentForm()
    if form.validate_on_submit():
        shipment = Shipment(
            sender_id=current_user.id,
            origin=form.origin.data,
            destination=form.destination.data,
            weight=form.weight.data,
            description=form.description.data,
            pickup_date=form.pickup_date.data,
            delivery_date=form.delivery_date.data,
            price=form.price.data
        )
        
        db.session.add(shipment)
        db.session.commit()
        
        flash('Spedizione pubblicata con successo!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('post_shipment.html', form=form)

@app.route('/browse-shipments')
@login_required
def browse_shipments():
    # Remove restriction - anyone can browse shipments now
    # Show only pending shipments
    shipments = Shipment.query.filter_by(status=ShipmentStatus.PENDING).order_by(Shipment.created_at.desc()).all()
    return render_template('browse_shipments.html', shipments=shipments)

@app.route('/shipment/<int:shipment_id>')
@login_required
def shipment_details(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    
    # Check if user has access to this shipment
    if (shipment.sender_id != current_user.id and shipment.transporter_id != current_user.id and shipment.status != ShipmentStatus.PENDING):
        flash('Accesso negato', 'error')
        return redirect(url_for('dashboard'))
    
    booking_form = BookingForm()
    tracking_form = TrackingUpdateForm()
    
    return render_template('shipment_details.html', 
                         shipment=shipment, 
                         booking_form=booking_form,
                         tracking_form=tracking_form)

@app.route('/book-shipment', methods=['POST'])
@login_required
def book_shipment():
    # Remove restriction - anyone can book shipments now
    form = BookingForm()
    if form.validate_on_submit():
        shipment = Shipment.query.get_or_404(form.shipment_id.data)
        
        if shipment.status != ShipmentStatus.PENDING:
            flash('Questa spedizione non è più disponibile', 'error')
            return redirect(url_for('browse_shipments'))
        
        # Update shipment
        shipment.transporter_id = current_user.id
        shipment.status = ShipmentStatus.BOOKED
        shipment.price = form.proposed_price.data
        
        db.session.commit()
        
        flash('Spedizione prenotata con successo!', 'success')
        return redirect(url_for('shipment_details', shipment_id=shipment.id))
    
    flash('Prenotazione fallita', 'error')
    return redirect(url_for('browse_shipments'))

@app.route('/payment/<int:shipment_id>')
@login_required
def payment(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if shipment.sender_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if shipment.status != ShipmentStatus.BOOKED:
        flash('Payment not available for this shipment', 'error')
        return redirect(url_for('shipment_details', shipment_id=shipment_id))
    
    form = PaymentForm()
    return render_template('payment.html', shipment=shipment, form=form)

@app.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    form = PaymentForm()
    shipment_id = request.form.get('shipment_id')
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if shipment.sender_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if form.validate_on_submit():
        # Create mock payment
        payment = Payment(
            shipment_id=shipment.id,
            amount=shipment.price,
            transaction_id=generate_transaction_id(),
            status='completed'
        )
        
        # Update shipment status
        shipment.status = ShipmentStatus.IN_TRANSIT
        
        # Add initial tracking update
        tracking_update = TrackingUpdate(
            shipment_id=shipment.id,
            latitude=generate_mock_coordinates()[0],
            longitude=generate_mock_coordinates()[1],
            location_name=shipment.origin,
            update_message='Package picked up and in transit'
        )
        
        db.session.add(payment)
        db.session.add(tracking_update)
        db.session.commit()
        
        flash('Payment processed successfully!', 'success')
        return redirect(url_for('track_shipment', shipment_id=shipment_id))
    
    flash('Payment failed', 'error')
    return render_template('payment.html', shipment=shipment, form=form)

@app.route('/track/<int:shipment_id>')
@login_required
def track_shipment(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    
    # Check access
    if shipment.sender_id != current_user.id and shipment.transporter_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    tracking_updates = shipment.tracking_updates.order_by(TrackingUpdate.timestamp.desc()).all()
    return render_template('track_shipment.html', shipment=shipment, tracking_updates=tracking_updates)

@app.route('/add-tracking-update', methods=['POST'])
@login_required
def add_tracking_update():
    form = TrackingUpdateForm()
    shipment_id = request.form.get('shipment_id')
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if shipment.transporter_id != current_user.id:
        flash('Only the assigned transporter can add tracking updates', 'error')
        return redirect(url_for('dashboard'))
    
    if form.validate_on_submit():
        tracking_update = TrackingUpdate(
            shipment_id=shipment.id,
            latitude=generate_mock_coordinates()[0],
            longitude=generate_mock_coordinates()[1],
            location_name=form.location_name.data,
            update_message=form.update_message.data
        )
        
        db.session.add(tracking_update)
        db.session.commit()
        
        flash('Tracking update added successfully!', 'success')
    
    return redirect(url_for('track_shipment', shipment_id=shipment_id))

@app.route('/mark-delivered/<int:shipment_id>')
@login_required
def mark_delivered(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if shipment.transporter_id != current_user.id:
        flash('Only the assigned transporter can mark as delivered', 'error')
        return redirect(url_for('dashboard'))
    
    shipment.status = ShipmentStatus.DELIVERED
    shipment.delivery_date = datetime.utcnow()
    
    # Add final tracking update
    tracking_update = TrackingUpdate(
        shipment_id=shipment.id,
        latitude=generate_mock_coordinates()[0],
        longitude=generate_mock_coordinates()[1],
        location_name=shipment.destination,
        update_message='Package delivered successfully'
    )
    
    db.session.add(tracking_update)
    db.session.commit()
    
    flash('Shipment marked as delivered!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/reviews/<int:shipment_id>')
@login_required
def reviews(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if shipment.status != ShipmentStatus.DELIVERED:
        flash('Reviews are only available for delivered shipments', 'error')
        return redirect(url_for('dashboard'))
    
    if shipment.sender_id != current_user.id and shipment.transporter_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    form = ReviewForm()
    existing_review = Review.query.filter_by(
        shipment_id=shipment_id,
        reviewer_id=current_user.id
    ).first()
    
    return render_template('reviews.html', 
                         shipment=shipment, 
                         form=form, 
                         existing_review=existing_review)

@app.route('/add-review', methods=['POST'])
@login_required
def add_review():
    form = ReviewForm()
    shipment_id = request.form.get('shipment_id')
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if form.validate_on_submit():
        # Determine who is being reviewed
        if current_user.id == shipment.sender_id:
            reviewee_id = shipment.transporter_id
        else:
            reviewee_id = shipment.sender_id
        
        # Check if review already exists
        existing_review = Review.query.filter_by(
            shipment_id=shipment_id,
            reviewer_id=current_user.id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this shipment', 'error')
            return redirect(url_for('reviews', shipment_id=shipment_id))
        
        review = Review(
            shipment_id=shipment_id,
            reviewer_id=current_user.id,
            reviewee_id=reviewee_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Review added successfully!', 'success')
    
    return redirect(url_for('reviews', shipment_id=shipment_id))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# API Routes for Real GPS Tracking

@app.route('/api/tracking/update', methods=['POST'])
@login_required
def api_tracking_update():
    """API endpoint to receive live GPS coordinates from transporter"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['shipment_id', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        shipment_id = data['shipment_id']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        accuracy = data.get('accuracy', 0)
        speed = data.get('speed', 0)
        heading = data.get('heading', 0)
        
        # Verify shipment exists and user is the transporter
        shipment = Shipment.query.get_or_404(shipment_id)
        if shipment.transporter_id != current_user.id:
            return jsonify({'error': 'Not authorized to update this shipment'}), 403
            
        # Create new tracking update
        tracking_update = TrackingUpdate(
            shipment_id=shipment_id,
            latitude=latitude,
            longitude=longitude,
            location_name=data.get('location_name', f"{latitude:.4f}, {longitude:.4f}"),
            update_message=f"Live GPS update - Accuracy: {accuracy:.0f}m"
        )
        
        db.session.add(tracking_update)
        
        # Update shipment status if not already in transit
        if shipment.status == ShipmentStatus.BOOKED:
            shipment.status = ShipmentStatus.IN_TRANSIT
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'tracking_id': tracking_update.id,
            'timestamp': tracking_update.timestamp.isoformat()
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid coordinate values'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tracking/start/<int:shipment_id>', methods=['POST'])
@login_required
def api_start_tracking(shipment_id):
    """Start GPS tracking for a shipment"""
    try:
        shipment = Shipment.query.get_or_404(shipment_id)
        
        # Verify user is the transporter
        if shipment.transporter_id != current_user.id:
            return jsonify({'error': 'Not authorized'}), 403
            
        # Check if shipment is in correct status
        if shipment.status not in [ShipmentStatus.BOOKED, ShipmentStatus.IN_TRANSIT]:
            return jsonify({'error': 'Shipment not ready for tracking'}), 400
            
        # Create initial tracking entry
        tracking_update = TrackingUpdate(
            shipment_id=shipment_id,
            location_name="Tracking Started",
            update_message="Live GPS tracking initialized"
        )
        
        db.session.add(tracking_update)
        
        # Update shipment status
        shipment.status = ShipmentStatus.IN_TRANSIT
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'GPS tracking started',
            'shipment_id': shipment_id,
            'status': shipment.status.value
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tracking/stop/<int:shipment_id>', methods=['POST'])
@login_required
def api_stop_tracking(shipment_id):
    """Stop GPS tracking for a shipment"""
    try:
        shipment = Shipment.query.get_or_404(shipment_id)
        
        # Verify user is the transporter
        if shipment.transporter_id != current_user.id:
            return jsonify({'error': 'Not authorized'}), 403
            
        # Create tracking entry
        tracking_update = TrackingUpdate(
            shipment_id=shipment_id,
            location_name="Tracking Stopped",
            update_message="GPS tracking has been stopped"
        )
        
        db.session.add(tracking_update)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'GPS tracking stopped',
            'shipment_id': shipment_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tracking/status/<int:shipment_id>')
@login_required
def api_tracking_status(shipment_id):
    """Get current tracking status for a shipment"""
    try:
        shipment = Shipment.query.get_or_404(shipment_id)
        
        # Verify user can access this shipment
        if shipment.sender_id != current_user.id and shipment.transporter_id != current_user.id:
            return jsonify({'error': 'Not authorized'}), 403
            
        # Get latest tracking updates
        latest_updates = TrackingUpdate.query.filter_by(shipment_id=shipment_id)\
            .order_by(TrackingUpdate.timestamp.desc())\
            .limit(10).all()
            
        updates_data = []
        for update in latest_updates:
            updates_data.append({
                'id': update.id,
                'latitude': update.latitude,
                'longitude': update.longitude,
                'location_name': update.location_name,
                'update_message': update.update_message,
                'timestamp': update.timestamp.isoformat()
            })
            
        return jsonify({
            'success': True,
            'shipment_id': shipment_id,
            'status': shipment.status.value,
            'updates': updates_data,
            'total_updates': len(updates_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/messages')
@app.route('/messages/<int:shipment_id>/<int:user_id>')
@login_required
def messages(shipment_id=None, user_id=None):
    # Get all conversations for current user
    conversations = []
    
    # Get shipments where user is involved
    user_shipments = Shipment.query.filter(
        (Shipment.sender_id == current_user.id) | 
        (Shipment.transporter_id == current_user.id)
    ).all()
    
    for shipment in user_shipments:
        # Determine the other user
        if shipment.sender_id == current_user.id and shipment.transporter_id:
            other_user = User.query.get(shipment.transporter_id)
        elif shipment.transporter_id == current_user.id:
            other_user = User.query.get(shipment.sender_id)
        else:
            continue
            
        if other_user:
            # Get last message and unread count
            last_message = Message.query.filter(
                Message.shipment_id == shipment.id,
                ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user.id)) |
                ((Message.sender_id == other_user.id) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.desc()).first()
            
            unread_count = Message.query.filter(
                Message.shipment_id == shipment.id,
                Message.sender_id == other_user.id,
                Message.receiver_id == current_user.id,
                Message.is_read == False
            ).count()
            
            conversation = {
                'shipment': shipment,
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': unread_count
            }
            conversations.append(conversation)
    
    # Sort by last message time
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else datetime.min, reverse=True)
    
    # Handle specific conversation
    current_conversation = None
    messages_list = []
    form = MessageForm()
    
    if shipment_id and user_id:
        shipment = Shipment.query.get_or_404(shipment_id)
        other_user = User.query.get_or_404(user_id)
        
        # Verify user has access to this conversation
        if (shipment.sender_id == current_user.id and shipment.transporter_id == user_id) or \
           (shipment.transporter_id == current_user.id and shipment.sender_id == user_id):
            
            current_conversation = {
                'shipment': shipment,
                'other_user': other_user
            }
            
            # Get messages for this conversation
            messages_list = Message.query.filter(
                Message.shipment_id == shipment_id,
                ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
                ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.asc()).all()
            
            # Mark messages as read
            Message.query.filter(
                Message.shipment_id == shipment_id,
                Message.sender_id == user_id,
                Message.receiver_id == current_user.id,
                Message.is_read == False
            ).update({'is_read': True})
            db.session.commit()
    
    return render_template('messages.html', 
                         conversations=conversations,
                         current_conversation=current_conversation,
                         messages=messages_list,
                         form=form)

@app.route('/send-message', methods=['POST'])
@login_required
def send_message():
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            shipment_id=form.shipment_id.data,
            sender_id=current_user.id,
            receiver_id=form.receiver_id.data,
            content=form.content.data
        )
        
        db.session.add(message)
        db.session.commit()
        
        flash('Messaggio inviato!', 'success')
        return redirect(url_for('messages', 
                              shipment_id=form.shipment_id.data, 
                              user_id=form.receiver_id.data))
    
    flash('Errore nell\'invio del messaggio', 'error')
    return redirect(url_for('messages'))

@app.route('/mark-messages-read', methods=['POST'])
@login_required
def mark_messages_read():
    data = request.get_json()
    if data and data.get('shipment_id') and data.get('sender_id'):
        Message.query.filter(
            Message.shipment_id == data['shipment_id'],
            Message.sender_id == data['sender_id'],
            Message.receiver_id == current_user.id,
            Message.is_read == False
        ).update({'is_read': True})
        db.session.commit()
        
    return jsonify({'status': 'success'})

@app.route('/request-shipment', methods=['POST'])
@login_required
def request_shipment():
    form = ShipmentRequestForm()
    if form.validate_on_submit():
        shipment = Shipment.query.get_or_404(form.shipment_id.data)
        
        # Check if shipment is available
        if shipment.status != ShipmentStatus.PENDING:
            flash('Questa spedizione non è più disponibile', 'error')
            return redirect(url_for('browse_shipments'))
        
        # Check if user is not the sender
        if shipment.sender_id == current_user.id:
            flash('Non puoi richiedere la tua stessa spedizione', 'error')
            return redirect(url_for('browse_shipments'))
        
        # Check if user already has a pending request
        existing_request = ShipmentRequest.query.filter_by(
            shipment_id=shipment.id,
            transporter_id=current_user.id,
            status=ShipmentRequestStatus.PENDING
        ).first()
        
        if existing_request:
            flash('Hai già inviato una richiesta per questa spedizione', 'warning')
            return redirect(url_for('shipment_details', shipment_id=shipment.id))
        
        # Redirect to recap screen before confirming
        return redirect(url_for('request_recap', 
                               shipment_id=shipment.id,
                               proposed_price=form.proposed_price.data,
                               message=form.message.data))
    
    flash('Errore nell\'invio della richiesta', 'error')
    return redirect(url_for('browse_shipments'))

@app.route('/request-recap/<int:shipment_id>')
@login_required
def request_recap(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    proposed_price = request.args.get('proposed_price', type=float)
    message = request.args.get('message', '')
    
    # Check if shipment is available
    if shipment.status != ShipmentStatus.PENDING:
        flash('Questa spedizione non è più disponibile', 'error')
        return redirect(url_for('browse_shipments'))
    
    # Check if user is not the sender
    if shipment.sender_id == current_user.id:
        flash('Non puoi richiedere la tua stessa spedizione', 'error')
        return redirect(url_for('browse_shipments'))
    
    # Check if user already has a pending request
    existing_request = ShipmentRequest.query.filter_by(
        shipment_id=shipment.id,
        transporter_id=current_user.id,
        status=ShipmentRequestStatus.PENDING
    ).first()
    
    if existing_request:
        flash('Hai già inviato una richiesta per questa spedizione', 'warning')
        return redirect(url_for('shipment_details', shipment_id=shipment.id))
    
    return render_template('request_recap.html', 
                         shipment=shipment, 
                         proposed_price=proposed_price,
                         message=message)

@app.route('/confirm-request', methods=['POST'])
@login_required
def confirm_request():
    shipment_id = request.form.get('shipment_id', type=int)
    proposed_price = request.form.get('proposed_price', type=float)
    message = request.form.get('message', '')
    
    shipment = Shipment.query.get_or_404(shipment_id)
    
    # Final validation
    if shipment.status != ShipmentStatus.PENDING:
        flash('Questa spedizione non è più disponibile', 'error')
        return redirect(url_for('browse_shipments'))
    
    if shipment.sender_id == current_user.id:
        flash('Non puoi richiedere la tua stessa spedizione', 'error')
        return redirect(url_for('browse_shipments'))
    
    existing_request = ShipmentRequest.query.filter_by(
        shipment_id=shipment.id,
        transporter_id=current_user.id,
        status=ShipmentRequestStatus.PENDING
    ).first()
    
    if existing_request:
        flash('Hai già inviato una richiesta per questa spedizione', 'warning')
        return redirect(url_for('shipment_details', shipment_id=shipment.id))
    
    # Create new request
    shipment_request = ShipmentRequest(
        shipment_id=shipment.id,
        transporter_id=current_user.id,
        proposed_price=proposed_price,
        message=message
    )
    
    db.session.add(shipment_request)
    db.session.commit()
    
    flash('Richiesta inviata con successo! Il mittente riceverà una notifica.', 'success')
    return redirect(url_for('shipment_details', shipment_id=shipment.id))

@app.route('/manage-requests/<int:shipment_id>')
@login_required
def manage_requests(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    
    # Check if user is the sender
    if shipment.sender_id != current_user.id:
        flash('Non hai i permessi per gestire questa spedizione', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all pending requests
    requests = ShipmentRequest.query.filter_by(
        shipment_id=shipment_id,
        status=ShipmentRequestStatus.PENDING
    ).order_by(ShipmentRequest.created_at.desc()).all()
    
    return render_template('manage_requests.html', 
                         shipment=shipment, 
                         requests=requests)

@app.route('/handle-request/<int:request_id>/<action>')
@login_required
def handle_request(request_id, action):
    request_obj = ShipmentRequest.query.get_or_404(request_id)
    shipment = request_obj.shipment
    
    # Check if user is the sender
    if shipment.sender_id != current_user.id:
        flash('Non hai i permessi per gestire questa richiesta', 'error')
        return redirect(url_for('dashboard'))
    
    if action == 'accept':
        # Accept the request
        request_obj.status = ShipmentRequestStatus.ACCEPTED
        
        # Update shipment with transporter info
        shipment.transporter_id = request_obj.transporter_id
        shipment.status = ShipmentStatus.BOOKED
        shipment.price = request_obj.proposed_price
        
        # Reject all other pending requests
        ShipmentRequest.query.filter_by(
            shipment_id=shipment.id,
            status=ShipmentRequestStatus.PENDING
        ).filter(ShipmentRequest.id != request_id).update({
            'status': ShipmentRequestStatus.REJECTED
        })
        
        db.session.commit()
        
        flash(f'Richiesta accettata! {request_obj.transporter.get_full_name()} è ora il trasportatore.', 'success')
        
        # Redirect to start conversation with accepted transporter
        return redirect(url_for('messages', shipment_id=shipment.id, user_id=request_obj.transporter_id))
    
    elif action == 'reject':
        request_obj.status = ShipmentRequestStatus.REJECTED
        db.session.commit()
        flash('Richiesta rifiutata', 'info')
    
    return redirect(url_for('manage_requests', shipment_id=shipment.id))
