import json
from .models import SaveSessionAuthUsers


class SessionUpdateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Если пользователь авторизован, то данные берем из бэкапа"""

        if request.user.is_authenticated:
            try:
                auth_object = SaveSessionAuthUsers.objects.get(user = request.user)
            except SaveSessionAuthUsers.DoesNotExist:
                request.session.update({'group_questions': []})
                return
            session_data_json = auth_object.session_data
            if session_data_json:
                session_data = {'group_questions': json.loads(session_data_json)}
                if request.session.get('group_questions') != session_data.get('group_questions'):
                    request.session.update(session_data)
            # elif not session_data_json and request.session.get('group_questions'):
            #     request.session.pop('group_questions', None)


