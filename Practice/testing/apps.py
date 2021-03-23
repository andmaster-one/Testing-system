from django.apps import AppConfig
import sys

class TestingConfig(AppConfig):
    name = 'testing'
    verbose_name = 'Сервис тестирования'

    def ready(self):   
        if 'runserver' in sys.argv or 'manage.py' not in sys.argv:
            from .models import Group
            groups_set = set(Group.objects.only('pk').values_list(flat = True))
            from .cache import GROUPS_SET_PK
            GROUPS_SET_PK.update(groups_set)
            import testing.signals
        
 