from django.shortcuts import render, redirect
from django.shortcuts import Http404
from .models import Group
from .forms import AnswerForm
from .cache import GROUPS_SET_PK
from .logic import (get_or_setup_session_group, get_session_group, get_session, 
                    setup_or_update_group_questions, get_current_question, 
                    get_rest, process_validation_answers,
                    update_session_with_answer, get_results)

def index(request):
    """ Стартовая страница выбора тестирования """
  
    groups = Group.objects.all()
    session = get_session(request) 
    finished_groups = set()   
    if session:        
        for group in session:
            if group.get('is_finished'):
                finished_groups.add(group['group_pk'])

    context = {'groups':groups, 'finished_groups': finished_groups}
    return render(request, 'testing/index.html', context)

def group_view(request, pk):
    '''Выборка вопросов и сохранение ответов для конкретного пользователя.

    Проверка сессии текщуего пользователя, выборка незавершенных вопросов,
    сохранение ответов в сессии базы данных
    '''

    if pk not in GROUPS_SET_PK:
        raise Http404

    _, group = get_or_setup_session_group(request, pk)
    current_question = get_current_question(group)

    if current_question is None:
        #Все вопросы в группе пройдены. Вернуть на страницу результатов группы. 
        #В сессию поставлен флаг завершения.
        request.session.modified = True
        return redirect('testing-service:group_result_url', pk=pk)
       
    #Получи общеее число вопроосов и число оставшихся
    number_questions, rest_questions = get_rest(group)

    if request.method == 'POST' and request.POST.get('token') == str(current_question.pk):
        form = AnswerForm(current_question, request.POST)
        if form.is_valid():
            answers = set(form.cleaned_data['variants_answers'])
            is_correct = process_validation_answers(current_question, answers)
            # Обновляем объект группы в сессии
            update_session_with_answer(group, is_correct) 
            request.session.modified = True
            return redirect(request.path_info)  
    else:
        form = AnswerForm(current_question)

    context = {'form' : form, 
               'rest_questions':rest_questions, 
               'number_questions' : number_questions }
    return render(request, 'testing/group.html', context)


def group_result_view(request, pk):
    """ Отображение результатов группы, если они есть """

    #Валидация на случай некорректных url
    if pk not in GROUPS_SET_PK:
        raise Http404

    #Валидация на случай попытки узнать несуществующий результат
    session, group = get_session_group(request, pk)
    if group is None or group == -1 or not group['is_finished']:
        raise Http404

    group_name = Group.objects.get(pk=pk).name
    len_correct_answers, len_incorrect_answers, number_questions, procent_success = get_results(group)

    context = {
                'group_name': group_name,
                'len_correct_answers': len_correct_answers,
                'len_incorrect_answers': len_incorrect_answers,
                'number_questions': number_questions,
                'procent_success': procent_success
              }

    return render(request, 'testing/group_result.html', context)


def overal_result_view(request): 
    """ Выводим общие результаты по всем тестирования """

    session = get_session(request)

    result = []

    if session:
        for group in session:
            if group.get('is_finished'):
                group_pk = group['group_pk']
                group_name = Group.objects.get(pk = int(group['group_pk'])).name
                len_correct_answers, _, number_questions, procent_success = get_results(group)
                result.append((group_name, len_correct_answers, number_questions, procent_success, group_pk))
 
    context = { 'result': result }
    return render(request, 'testing/overall_result.html', context)

    # session = { 
    #     'group_questions' :  [
    #             {
    #                 'group_pk' : 1,
    #                 'process_questions' : [],
    #                 'current_question' : None,
    #                 'correct_answers': [1,2,3,4],
    #                 'incorrect_answers' : [5,6],
    #                 'overall score': 12,
    #                 'is_finished' : True,
    #             },
    #         ]
    # }
