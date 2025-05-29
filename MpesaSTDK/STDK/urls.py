from django.urls import path
from. import views
urlpatterns = [
    path('', views.index, name='index'),
    # path to prompt stk push
    path('', views.stk_push, name='stk_push'),
    # routes for status checking
    path('waiting/<int:transaction_id>/', views.waiting, name='waiting'),
    # this is the path that will receive the status of our transaction
    path('callback', views.callback, name='callback'),
    # this is the route that confirms the status of the above feedback/callback results
    path('check-status/<int:transaction_id>/', views.check_status, name='check_status'),
    path('payment_success', views.payment_success, name='payment_success'),
    path('payment_failed', views.payment_failed, name='payment_failed'),
    path('payment_cancelled', views.payment_cancelled, name='payment_cancelled'),
]