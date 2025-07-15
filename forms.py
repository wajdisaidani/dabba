from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FloatField, TextAreaField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo
from wtforms.widgets import DateTimeLocalInput
from models import UserType
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    first_name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Cognome', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Telefono', validators=[Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Conferma Password', 
                                   validators=[DataRequired(), EqualTo('password', message='Le password devono corrispondere')])

class ShipmentForm(FlaskForm):
    origin = StringField('Luogo di Ritiro', validators=[DataRequired(), Length(max=200)])
    destination = StringField('Luogo di Consegna', validators=[DataRequired(), Length(max=200)])
    weight = FloatField('Peso (kg)', validators=[DataRequired(), NumberRange(min=0.1, max=10000)])
    description = TextAreaField('Descrizione del Pacco', validators=[Length(max=500)])
    pickup_date = DateTimeField('Data e Ora di Ritiro', 
                               validators=[DataRequired()], 
                               widget=DateTimeLocalInput(),
                               format='%Y-%m-%dT%H:%M')
    delivery_date = DateTimeField('Data e Ora di Consegna Preferita', 
                                 widget=DateTimeLocalInput(),
                                 format='%Y-%m-%dT%H:%M')
    price = FloatField('Prezzo Offerto (€)', validators=[DataRequired(), NumberRange(min=1)])

class BookingForm(FlaskForm):
    shipment_id = HiddenField('ID Spedizione', validators=[DataRequired()])
    proposed_price = FloatField('Il Tuo Prezzo (€)', validators=[DataRequired(), NumberRange(min=1)])

class PaymentForm(FlaskForm):
    card_number = StringField('Numero Carta', validators=[DataRequired(), Length(min=16, max=16)])
    expiry_month = SelectField('Mese', 
                              choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)],
                              validators=[DataRequired()])
    expiry_year = SelectField('Anno',
                             choices=[(str(i), str(i)) for i in range(2024, 2035)],
                             validators=[DataRequired()])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=4)])
    cardholder_name = StringField('Nome del Titolare', validators=[DataRequired()])

class ReviewForm(FlaskForm):
    rating = SelectField('Valutazione', 
                        choices=[(5, '5 - Eccellente'), (4, '4 - Buono'), (3, '3 - Medio'), (2, '2 - Scarso'), (1, '1 - Pessimo')],
                        validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Commento Recensione', validators=[Length(max=1000)])

class TrackingUpdateForm(FlaskForm):
    location_name = StringField('Posizione Attuale', validators=[DataRequired(), Length(max=200)])
    update_message = StringField('Aggiornamento Stato', validators=[DataRequired(), Length(max=500)])

class ShipmentRequestForm(FlaskForm):
    proposed_price = FloatField('Prezzo Proposto (€)', validators=[DataRequired(), NumberRange(min=1)])
    message = TextAreaField('Messaggio (opzionale)', validators=[Length(max=500)])
    shipment_id = HiddenField('Spedizione', validators=[DataRequired()])

class MessageForm(FlaskForm):
    content = TextAreaField('Messaggio', validators=[DataRequired(), Length(max=1000)])
    receiver_id = HiddenField('Destinatario', validators=[DataRequired()])
    shipment_id = HiddenField('Spedizione', validators=[DataRequired()])
