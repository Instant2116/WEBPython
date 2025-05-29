from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')


class RegistrationForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Підтвердіть пароль', validators=[DataRequired(), EqualTo('password',
                                                                                               message='Паролі повинні співпадати')])
    submit = SubmitField('Зареєструватися')


class ItemForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Опис', validators=[DataRequired()])
    submit = SubmitField('Зберегти знайдений предмет')


class LostItemForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Опис', validators=[DataRequired()])
    submit = SubmitField('Зберегти втрачений предмет')


class DeleteForm(FlaskForm):
    pass


class RoleForm(FlaskForm):
    name = StringField('Назва ролі', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Зберегти роль')


class UserEditForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    role_id = SelectField('Роль', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Оновити користувача')
