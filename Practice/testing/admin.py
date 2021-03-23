import json
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.html import format_html
from django import forms
from django.contrib import admin
from nested_inline.admin import NestedStackedInline
from django.forms.models import BaseInlineFormSet
from .admin_utils import CustomNestedModelAdmin
from .models import Group, Question, Answer, SaveSessionAuthUsers
from .logic import get_results

class AnswerInlineForm(BaseInlineFormSet):
    """
    Answer nested inline formset
    """
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validation answers formset: all or nothing is_true answers are not valid
        """
        if len(self.forms) > 1:  
            list_fields__is_true = []    
            for form in self.forms:
                if form.cleaned_data.get('is_true') is not None:
                    list_fields__is_true.append(form.cleaned_data.get('is_true'))
            if all(list_fields__is_true) or not any(list_fields__is_true):                
                if self.request is not None:                
                    messages.error(self.request, 'НЕПРАВИЛЬНО ЗАПОЛНЕНА ФОРМА')
                raise ValidationError('ОШИБКА В ДАННОЙ ФОРМЕ')
                    

class AnswerInline(NestedStackedInline):  
    """
    Admin answers nested class
    """ 
    model = Answer
    extra = 1
    fk_name = 'question'
    formset = AnswerInlineForm
  
class QuestionInline(NestedStackedInline):
    """
    Admin questions nested class
    """     
    model = Question
    extra = 1
    fk_name = 'group'
    inlines = [AnswerInline]

class GroupAdmin(CustomNestedModelAdmin):
    """
    Admin group_questions nested class
    """     
    model = Group
    inlines = [QuestionInline]
    list_display = ['name']
    save_on_top = True
    
    def get_actions(self, request):
        """
        Exclude 'delete_selected' from actions, because it doesnt't call model delete method
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(Group, GroupAdmin)

class QuestionAdmin(CustomNestedModelAdmin):
    """
    Admin questions class
    """ 
    model = Question
    inlines = [AnswerInline]
    list_display = ['name', 'group']
    list_editable = ['group']
    list_filter = ['group']

admin.site.register(Question, QuestionAdmin)

class AnswerModel(admin.ModelAdmin):
    """
    Admin answers class
    """ 
    list_display = ['name', 'question', 'is_true', 'test_group',]
    list_filter = ['is_true', 'question', 'question__group', ]
    list_editable = ['is_true']
    list_display_links = ['name',]
    actions = ['make_true', 'make_false',]
    fields = ('name', 'question', 'is_true')  

    def test_group(self, obj):
        return obj.question.group
    
    test_group.short_description = 'Группа'
    
    def make_true(self, request, queryset):
        queryset.update(is_true=True)
    make_true.short_description = "Поставить, как верные"

    def make_false(self, request, queryset):
        queryset.update(is_true=False)
    make_false.short_description = "Поставить, как неверные"

admin.site.register(Answer, AnswerModel)


class SaveSessionAuthUsersForm(forms.ModelForm):
    """
    User results form
    """
    class Meta:
        fields = ('session_data',)
    
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)                     
        current_test = SaveSessionAuthUsersModel.formated_results(self=None, obj=kwargs['instance'], to_list=True)
        
        request = self.request
        if not current_test or isinstance(current_test, str):
            messages.warning(request, 'Не прошел ни одного теста!')
            current_test = []

        self.fields['session_data'] = forms.TypedMultipleChoiceField( 
                            label='Выберете тест',
                            required=False,
                            widget=forms.CheckboxSelectMultiple(),
                            choices = current_test,
                            coerce = int,
                            help_text='Выберете один или несколько тестов для удаления',                            
                            )
    
    def save(self, *args, **kwargs):
        session_data = self.cleaned_data['session_data']
        this_obj = super().save(*args, **kwargs)
        try:
            session_obj = self._meta.model.objects.get(pk=this_obj.pk)
            session_obj_data = json.loads(session_obj.session_data)
            session_obj_data_new = []
            for group in session_obj_data:
                if group['group_pk'] not in session_data:
                    session_obj_data_new.append(group)
            session_obj_data = json.dumps(session_obj_data_new)
        except:
            session_obj_data = []
        this_obj.session_data = session_obj_data
        this_obj.save()    
        return this_obj


class SaveSessionAuthUsersModel(admin.ModelAdmin):
    """ User's result admin class """

    list_display = ['user_name', 'formated_results']
    form = SaveSessionAuthUsersForm
    fields = ('user_name', 'session_data', )
    readonly_fields = ('user_name',)

    def user_name(self, obj):
        return ' '.join([obj.user.first_name, obj.user.last_name]).strip() or obj.user.username
    
    user_name.short_description = 'Пользователь'

    def get_form(self, request, obj=None, **kwargs):         
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form
        
    def get_results(self, obj):
        result_list = []
        session_data_json = obj.session_data
        if session_data_json:
            groups = json.loads(session_data_json)
            for group in groups:
                if group.get('is_finished'): 
                    result = {}        
                    group_pk = group['group_pk']           
                    group_name = Group.objects.get(pk = int(group['group_pk'])).name
                    len_correct_answers, _, number_questions, procent_success = get_results(group)
                    result.update({
                        'group_name':group_name,
                        'group_pk':group_pk,
                        'len_correct_answers':len_correct_answers,
                        'number_questions':number_questions,
                        'procent_success':procent_success,
                        })
                    result_list.append(result)                    
        return result_list
    
    def formated_results(self, obj, to_list=False):
        result_list = SaveSessionAuthUsersModel.get_results(self=None, obj=obj)
        if not result_list:
            return format_html('<b style="color:red"> Не прошел ни одного теста! </b>')
        output_result = ''
        output_list = []
        for result in result_list:
            output_string = f"<span><strong>{result['group_name']}</strong>: всего вопросов - {result['number_questions']}, правильных - {result['len_correct_answers']} или <b style=\"color:red\">{result['procent_success']}% </b>.<br></span>"
            output_result += output_string
            if to_list:
                output_list.append((result['group_pk'], format_html(output_string)))        
        if to_list:
            return output_list
        return format_html(output_result)
   
    formated_results.short_description = "Результаты"
 
admin.site.register(SaveSessionAuthUsers, SaveSessionAuthUsersModel)
admin.site.site_title = 'Сервис тестирования'
admin.site.site_header = 'Сервис тестирования'
