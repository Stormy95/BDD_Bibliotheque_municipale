from django.urls import path

from . import views

app_name = 'library_app'
urlpatterns = [
    path('', views.index, name='index')
]

urlpatterns += [
    path('monespace/', views.board, name='board'),
    ]

urlpatterns += [
    path(r'^booking/(?P<reference_id>[0-9]+)/', views.booking, name='booking'),
    ]

urlpatterns += [
    path('booking/no_subscription/', views.no_subscription, name='no_subscription'),
    ]

urlpatterns += [
    path('subscribe/', views.subscribe, name='subscribe'),
    ]