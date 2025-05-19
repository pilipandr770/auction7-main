from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class ProposalForm(FlaskForm):
    title = StringField('Назва', validators=[DataRequired()])
    description = TextAreaField('Опис', validators=[DataRequired()])
    submit = SubmitField('Створити пропозицію')
