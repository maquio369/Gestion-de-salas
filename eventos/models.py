from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Sala(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class Evento(models.Model):
    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    nombre = models.CharField(max_length=200)
    fecha_hora = models.DateTimeField()
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True)
    
    requiere_laptop = models.BooleanField(default=False)
    requiere_proyector = models.BooleanField(default=False)
    
    numero_laptop = models.CharField(max_length=50, blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programado')
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['fecha_hora']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def es_hoy(self):
        return self.fecha_hora.date() == timezone.now().date()
    
    @property
    def es_manana(self):
        from datetime import timedelta
        manana = timezone.now().date() + timedelta(days=1)
        return self.fecha_hora.date() == manana

class Nota(models.Model):
    COLOR_CHOICES = [
        ('#009885', 'Verde'),
        ('#C90166', 'Rosa'),
        ('#AE192D', 'Rojo'),
        ('#ff6b35', 'Naranja'),
        ('#6c757d', 'Gris'),
        ('#0052cc', 'Azul'),
        ('#6f42c1', 'Morado'),
        ('#e83e8c', 'Fucsia'),
    ]
    
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#009885')
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_modificacion']
    
    def __str__(self):
        return self.titulo

