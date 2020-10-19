from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL

from app.website.db import check_for_username, check_for_email

class RegistrationForm(FlaskForm):
    """
    Form for managing user sign ups
    """
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = check_for_username(username.data)
        if user:
            raise ValidationError("That username is taken. Choose a different one!")

    def validate_email(self, email):
        user = check_for_email(email.data)
        if user:
            raise ValidationError("There is already an account associated with that email!")


class LoginForm(FlaskForm):
    """
    Form for managing user log ins
    """
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class PostForm(FlaskForm):
    """
    Form for posting content
    """
    title = StringField("Title  (Max 75 chars)", validators=[DataRequired(), Length(max=75)])
    misinfo = TextAreaField("Misinformation (Max 150 chars)", validators=[DataRequired(), Length(max=150)])
    link = StringField("Proof Link", validators=[DataRequired(), URL()])
    info = TextAreaField("Information (Max 150 chars)", validators=[DataRequired(), Length(max=150)])
    additional = TextAreaField("Any Additional Proof", validators=[DataRequired()])
    submit = SubmitField("Post")


class CommentForm(FlaskForm):
    """
    For for creating comments
    """
    content = TextAreaField("Comment", validators=[DataRequired()])
    select = SelectField("Do you agree with the post?", choices=[("Agree", "Agree"), ("Disagree", "Disagree")])
    submit = SubmitField("Post")
    
