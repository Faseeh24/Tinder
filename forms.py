from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, SelectMultipleField, DateField, FileField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[Optional(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[Optional()])
    match_preference = SelectField('Match Preference', choices=[('male', 'Male'), ('female', 'Female'), ('both', 'Both')], validators=[Optional()])
    profession = StringField('Profession', validators=[Optional(), Length(max=100)])
    education_level = StringField('Education Level', validators=[Optional(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    about_me = TextAreaField('About Me', validators=[Optional(), Length(max=500)])
    interests = SelectMultipleField('Interests', choices=[
        ('sports', 'Sports'), ('music', 'Music'), ('travel', 'Travel'), ('reading', 'Reading'),
        ('movies', 'Movies'), ('cooking', 'Cooking'), ('fitness', 'Fitness'), ('gaming', 'Gaming'),
        ('art', 'Art'), ('technology', 'Technology'), ('fashion', 'Fashion'), ('photography', 'Photography')
    ], validators=[Optional()])
    selected_interests = HiddenField('Selected Interests')
    profile_photo = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'), Optional()])
    submit = SubmitField('Save Profile')
