from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
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
            'estado': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_hora = cleaned_data.get("fecha_hora")
        sala = cleaned_data.get("sala")

        if fecha_hora and sala:
            # Definimos la duración del evento (1 hora y 58 minutos para dar un margen)
            duracion_evento = timedelta(hours=1, minutes=58)
            fin_evento = fecha_hora + duracion_evento

            # Buscamos eventos que se superpongan en la misma sala.
            # Un evento se superpone si:
            # - Su inicio está dentro de nuestro nuevo evento.
            # - Su fin está dentro de nuestro nuevo evento.
            # - Nuestro nuevo evento está completamente dentro de otro evento.
            eventos_en_conflicto = Evento.objects.filter(
                sala=sala,
                fecha_hora__lt=fin_evento,
                fecha_hora__gte=fecha_hora - duracion_evento
            ).exclude(estado__in=['finalizado', 'cancelado'])

            # Si estamos editando, debemos excluir el propio evento de la comprobación.
            if self.instance and self.instance.pk:
                eventos_en_conflicto = eventos_en_conflicto.exclude(pk=self.instance.pk)

            if eventos_en_conflicto.exists():
                # Obtenemos el primer evento en conflicto para mostrar más detalles.
                conflicto = eventos_en_conflicto.first()
                raise ValidationError(
                    f"La sala '{sala.nombre}' ya está ocupada en ese horario. "
                    f"Hay un conflicto con el evento '{conflicto.nombre}' programado a las {timezone.localtime(conflicto.fecha_hora).strftime('%H:%M') }."
                )

        return cleaned_data

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['titulo', 'contenido', 'color']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la nota'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Contenido de la nota'}),
            'color': forms.HiddenInput(attrs={'id': 'id_color'}),
        }
