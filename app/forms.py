from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Add Product')