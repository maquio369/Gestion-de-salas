from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('crear/', views.crear_evento, name='crear_evento'),
    path('editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    path('calendario/', views.calendario_eventos, name='calendario'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('finalizar/<int:evento_id>/', views.finalizar_evento, name='finalizar_evento'),
    path('notas/', views.notas, name='notas'),
    path('notas/crear/', views.crear_nota, name='crear_nota'),
    path('notas/editar/<int:nota_id>/', views.editar_nota, name='editar_nota'),
    path('notas/eliminar/<int:nota_id>/', views.eliminar_nota, name='eliminar_nota'),
    path('imprimir-manana/', views.imprimir_eventos_manana, name='imprimir_eventos_manana'),
]
