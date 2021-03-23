import json
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from .models import SaveSessionAuthUsers
from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from allauth.socialaccount.signals import pre_social_login


@receiver(pre_social_login)
def handler_provider_login(*args, **kwargs):
    """ Очистка сессии перед логином """
    
    kwargs.get('request').session.flush()
    print('Handle')

@receiver(post_save, sender=Session)
def handler_change_session(sender, instance, created, **kwargs):
    """ Для авторизованного пользователя делаем бэкап сессии при каждом измени """

    user_id = instance.get_decoded().get('_auth_user_id')
    if user_id is not None:  
        user = User.objects.get(pk = user_id)        
        auth_object, created = SaveSessionAuthUsers.objects.get_or_create(user = user)

        if not created: 
            group_questions = instance.get_decoded().get('group_questions')
            if group_questions:
                js = json.dumps(group_questions)
                auth_object.session_data = js
                auth_object.save()


