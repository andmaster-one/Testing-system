from .models import Question, Answer

def get_session(request):
    """ Проверяем, есть ли сессия пользователя, 
        если есть, то возвращаем ее, иначе None """

    if request.session.get('group_questions'):
        return request.session.get('group_questions')
    else:
        return None 


def set_session(request):
    """ Инициализируем и возвращаем сессию пользователя списком """

    request.session['group_questions'] = []
    return request.session.get('group_questions')

def get_or_setup_session_group(request, pk):
    """ Ищем объект группы в сессии. Если не находим, то инициализируем сессию. 
        Возвращем кортеж сессии и группы (sesson, group): """

    session, group = get_session_group(request, pk)
    if session is None or group == -1:
            if session is None:
                session = set_session(request) 
            group = setup_or_update_group_questions(session, pk) 
            #request.session.modified = True

    return session, group


def get_session_group(request, pk): 
    """ Ищем объект группы в сессии. 
          Возвращем кортеж сессии и группы (sesson, group): 
          (session, group) = (None, None) - отсуствует сессия и группа
          (session, group) = (session, -1) - отсуствует группа в сессии
          (session, group) = (session, group) - группа в сессии """ 

    session = get_session(request)
    if session:
        group = _get_group_(session, pk)
        return session, group
    return None, None


def _get_group_(session, pk):
    """ Возвращаем объект группы или -1, если не находим """ 

    for group in session:
        if group.get('group_pk') == pk:
            return group
    return -1


def _get_group_all_questions(pk):
    """ Вернуть queryset всех вопросов группы с заданным pk """

    return Question.objects.filter(group_id = pk)







def setup_or_update_group_questions(session, pk, update = None):
    """ Устанавливаем новый объект группы вопросов в сессию """ 

    questions_list = list(_get_group_all_questions(pk).values_list('pk', flat=True))

    group_object = {
                        'group_pk' : pk,
                        'process_questions' : questions_list,
                        'current_question_pk' : None,
                        'correct_answers': [],
                        'incorrect_answers' : [],
                        'overall score': None,
                        'is_finished' : False,
                    }

    if update == True:
        group = _get_group_(session, pk)
        if group != -1:
            group.update(group_object)
    else:    
        session.append(group_object)
    return group_object


def _get_current_question_pk(group):
    """ Получаем pk текущего вопроса из группы 
    
        Проверяем, текущий вопрос по ключу 'current_question_pk', если находим, то возвращаем.
        Если не находим, то пытаемся взять их очереди вопрос из 'process_questions' и сохранить
        в 'current_question_pk'. Вопрос из очереди удаляется. Если очередь пуста, то тест закончен
        и возвращаем None. """    

    if group['current_question_pk']:
        return group['current_question_pk']

    try:
        current_question_pk = group['process_questions'].pop()
        group['current_question_pk'] = current_question_pk

    # Исключение возникает только в случае завершение теста.
    except IndexError:        
        return None
    
    return current_question_pk


def get_current_question(group):
    """ Получаем объект вопроса из группы. Если все вопросов группе нет, то тест пройден, ставим флаг. """

    current_question_pk = _get_current_question_pk(group)

    if current_question_pk is None:
        group['is_finished'] = True
        return None

    try:
        current_question = Question.objects.get(pk = current_question_pk)
    except Question.DoesNotExist:
        # Сюда попадаем, если вопрос удалили из базы данных, после установки сессии пользователя
        return False    #TODO Redirect to Question.DoesNotExist page

    except Question.MultipleObjectsReturned:
        return False    #TODO Redirect to Question.MultipleObjectsReturned page
    
    return current_question


def get_lengths_questions(group):
    """ Возвращает кортеж длин списков pk вопросов на 
    которые даны правильные и неправильные ответы """
    
    len_incorrect_answers = len(group['incorrect_answers'])
    len_correct_answers = len(group['correct_answers'])
    return len_correct_answers, len_incorrect_answers


def get_rest(group):
    """ Возвращает общеее число вопроосов и число оставшихся """
    
    len_correct_answers, len_incorrect_answers = get_lengths_questions(group)
    len_process_questions = len(group['process_questions'])
    number_questions = len_incorrect_answers + len_process_questions + len_correct_answers + 1
    rest_questions = number_questions - len(group['process_questions'])
    return number_questions, rest_questions 


def process_validation_answers(current_question, answers):
    """ Проверка ответовов. Возвращаем True, если верно, False, если нет """ 

    correct_answers = set(Answer.objects.filter(question=current_question, is_true = True).values_list('pk', flat=True))
    if answers == correct_answers:
        return True
    else:
        return False

def update_session_with_answer(group, is_correct):
    """ Обновляем объект группы в сессии ответом на вопрос
        Перемешаем текущий вопрос, как овеченный в соответствующий список """

    current_question_pk = group['current_question_pk']

    if is_correct:
        group['correct_answers'].append(current_question_pk)
    else:
        group['incorrect_answers'].append(current_question_pk)

    group['current_question_pk'] = None


def get_results(group): 
    len_correct_answers, len_incorrect_answers = get_lengths_questions(group)
    number_questions = len_correct_answers + len_incorrect_answers
    procent_success = int((len_correct_answers/number_questions)*100)
    return len_correct_answers, len_incorrect_answers, number_questions, procent_success

#     # session = { 
#     #     'group_questions' :  [
#     #             {
#     #                 'group_pk' : 1,
#     #                 'process_questions' : [],
#     #                 'current_question_pk' : None,
#     #                 'correct_answers': [1,2,3,4],
#     #                 'incorrect_answers' : [5,6],
#     #                 'overall score': 12,
#     #                 'is_finished' : True,
#     #             },
#     #         ]
#     # }
