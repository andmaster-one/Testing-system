from django import forms
from django.core.exceptions import ValidationError
from allauth.account.forms import LoginForm

class MyCustomLoginForm(LoginForm):
    """ Login Form """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class':'form-control', 'placeholder':'login'})
        self.fields['password'].widget.attrs.update({'class':'form-control', 'placeholder':'password'})

    def login(self, *args, **kwargs):
        request = args[0]
        request.session.flush()  
        return super(MyCustomLoginForm, self).login(*args, **kwargs)


class AnswerForm(forms.Form):
       
    def __init__(self, current_question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = current_question.name
        self.group = current_question.group
        current_answers = current_question.answers.all()
        self.count = current_question.answers.count()
        answers_choices = [ (answer.pk, answer.name) for answer in current_answers ]

        self.fields['token'] = forms.IntegerField(widget=forms.HiddenInput, initial=current_question.pk)
        self.fields['variants_answers'] = forms.TypedMultipleChoiceField( 
                            label='Выберете один или несколько ответов',
                            required=False,
                            widget=forms.CheckboxSelectMultiple(),
                            choices = answers_choices,
                            coerce = int,
                            help_text='Выберете один или несколько вариантов ответов',                            
                            )
        self.fields['variants_answers'].widget.attrs.update({'class':'form-check-input'})

    def clean_variants_answers(self):
        """ Валидация ответов, чтобы не были все ответы правильные и был, 
        хотя бы один правильный """

        variants_answers = self.cleaned_data['variants_answers']
        if (len(variants_answers) >= self.count):
            raise ValidationError('Все варианты ответов не могут быть правильными!')        
        elif (len(variants_answers) == 0):
            raise ValidationError('Выберете хотя бы один вариант ответа!')
        return variants_answers


        

        

        

        

   