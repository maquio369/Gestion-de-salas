from django import forms
from .models import Evento, Nota

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'nombre',
            'fecha_hora',
            'sala',
            'observaciones',
            'requiere_laptop',
            'requiere_proyector',
            'numero_laptop',
            'estado',
        ]
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['titulo', 'contenido', 'color']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la nota'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Contenido de la nota'}),
            'color': forms.HiddenInput(attrs={'id': 'id_color'}),
        }
