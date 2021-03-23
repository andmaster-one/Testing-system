from django.urls import path
from .views import index, group_view, group_result_view, overal_result_view
#, register_view, logout_view, login_view


app_name = 'testing-service'

urlpatterns = [
    path('', index, name = 'index_url'),
    path('group/<int:pk>', group_view, name = 'group_url'),    
    path('group_result/<int:pk>', group_result_view, name = 'group_result_url'), 
    path('overall_result/', overal_result_view, name = 'overal_result_url'),
 
]


