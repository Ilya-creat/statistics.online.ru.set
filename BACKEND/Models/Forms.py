from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email("Некорректный Email")], render_kw={"placeholder": "Email"})
    psw = PasswordField("Пароль", validators=[DataRequired(), Length(min=5, max=100, message="Пароль должен содержать "
                                                                                             "не менее 5 и не более "
                                                                                             "100 символов")],
                        render_kw={"placeholder": "Пароль"})
    remember = BooleanField("Запоминть меня", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired(), Length(min=3, max=100, message="Имя должно содержать "
                                                                                         "не менее 3 и не более "
                                                                                         "100 символов")],
                       render_kw={"placeholder": "Имя"})
    surname = StringField("Фамилия", validators=[DataRequired(), Length(min=3, max=100,
                                                                        message="Фамилия должна содержать "
                                                                                "не менее 3 и не более "
                                                                                "100 символов")],
                          render_kw={"placeholder": "Фамилия"})
    email = StringField("Email", validators=[Email("Некорректный Email")], render_kw={"placeholder": "Email"})
    login = StringField("Логин", validators=[DataRequired(), Length(min=4, max=100,
                                                                    message="Логин должен содержать "
                                                                            "не менее 4 и не более "
                                                                            "100 символов")],
                        render_kw={"placeholder": "Логин"})
    psw1 = PasswordField("Пароль", validators=[DataRequired(), Length(min=5, max=100, message="Пароль должен содержать "
                                                                                              "не менее 5 и не более "
                                                                                              "100 символов")],
                         render_kw={"placeholder": "Пароль"})
    psw2 = PasswordField("Повтор пароля",
                         validators=[DataRequired(),
                                     EqualTo('psw1', message="Пароли не совпадают")],
                         render_kw={"placeholder": "Повтор пароля"})
    submit = SubmitField("Регистрация")


class RenameProfile(FlaskForm):
    name = StringField("Имя", validators=[DataRequired(), Length(min=3, max=100, message="Имя должно содержать "
                                                                                         "не менее 3 и не более "
                                                                                         "100 символов")],
                       render_kw={"placeholder": "Имя"})
    surname = StringField("Фамилия", validators=[DataRequired(), Length(min=3, max=100,
                                                                        message="Фамилия должна содержать "
                                                                                "не менее 3 и не более "
                                                                                "100 символов")],
                          render_kw={"placeholder": "Фамилия"})
    email = StringField("Email", validators=[Email("Некорректный Email")], render_kw={"placeholder": "Email"})
    login = StringField("Логин", validators=[DataRequired(), Length(min=4, max=100,
                                                                    message="Логин должен содержать "
                                                                            "не менее 4 и не более "
                                                                            "100 символов")],
                        render_kw={"placeholder": "Логин"})
    submit = SubmitField("Изменить даненые")
