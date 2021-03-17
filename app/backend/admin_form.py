from wtforms import TextField
from wtforms.widgets import TextInput

class NameWidget(TextInput):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' col-md-12'
        else:
            kwargs.setdefault('class', 'col-md-12')
        return super(NameWidget, self).__call__(field, **kwargs)

class NameField(TextField):
    widget = NameWidget()
