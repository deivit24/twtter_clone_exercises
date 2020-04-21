from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired(), Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for Editing users."""

    username = StringField('Username', validators=[Optional(), Length(max=20, message=" Username must be less than %(max)d characters long")])
    email = StringField('E-mail', validators=[Optional(), Email()])
    bio = StringField('Bio', validators=[Optional(), Length(max=1000, message=" Bio must be less than %(max)d characters long")])
    image_url = StringField('Image URL', validators=[Optional()])
    header_image_url = StringField('Header Image URL', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message=" Password must be more than %(min)d characters long")])
  

class EditPasswordForm(FlaskForm):
    """Form for changing existing user's password."""

    old_password = PasswordField('Current Password', validators=[Length(min=6)])
    new_password = PasswordField('New Password', validators=[Length(min=6), EqualTo('confirm', 'New passwords much match!')])
    confirm = PasswordField('Confirm New Password', validators=[Length(min=6)])
