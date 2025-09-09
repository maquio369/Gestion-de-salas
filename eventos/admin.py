from django.contrib import admin
from .models import Sala, Evento

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    search_fields = ('nombre',)
    list_filter = ('activa',)

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_hora', 'sala', 'estado', 'creado_por')
    search_fields = ('nombre', 'sala__nombre')
    list_filter = ('estado', 'fecha_hora')
