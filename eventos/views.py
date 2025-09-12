from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from .models import Evento, Nota, Sala
from .forms import EventoForm, NotaForm

def es_admin(user):
    """Verifica si el usuario es superusuario o staff."""
    return user.is_superuser or user.is_staff

def es_gestor_o_admin(user):
    """Verifica si el usuario es admin o pertenece al grupo 'Gestor de Eventos'."""
    return es_admin(user) or user.groups.filter(name='Gestor de Eventos').exists()


class CustomLoginView(LoginView):
    """Vista de login personalizada que redirige con mensaje de bienvenida"""
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard') + '?welcome=1'

def actualizar_estados_eventos():
    """Actualiza automáticamente los estados de los eventos"""
    ahora = timezone.localtime()
    
    # Cambiar eventos programados a activo cuando empiecen
    eventos_a_iniciar = Evento.objects.filter(
        fecha_hora__lte=ahora,
        estado='programado'
    )
    eventos_a_iniciar.update(estado='activo')
    
    # Cambiar eventos activos a finalizado después de 2 horas
    hace_2_horas = ahora - timedelta(hours=2)
    eventos_a_finalizar = Evento.objects.filter(
        fecha_hora__lte=hace_2_horas,
        estado='activo'
    )
    eventos_a_finalizar.update(estado='finalizado')

@login_required
def dashboard(request):
    # Si el usuario no es admin (superusuario/staff), redirigirlo al calendario.
    if not es_admin(request.user):
        return redirect('calendario')


    # Actualizar estados automáticamente
    actualizar_estados_eventos()
    
    hoy = timezone.localdate()
    ahora = timezone.localtime()
    manana = hoy + timedelta(days=1)

    # Eventos activos (todos los eventos con estado activo)
    eventos_encurso = Evento.objects.filter(
        estado='activo'
    ).order_by('fecha_hora')

    eventos_hoy = Evento.objects.filter(
        fecha_hora__date=hoy, 
        estado='programado'
    ).order_by('fecha_hora')
    
    eventos_manana = Evento.objects.filter(
        fecha_hora__date=manana, 
        estado='programado'
    ).order_by('fecha_hora')
    
    eventos_finalizados_hoy = Evento.objects.filter(
        fecha_hora__date=hoy, 
        estado='finalizado'
    ).order_by('-fecha_hora')

    # Detectar si es un login reciente (viene del login)
    show_welcome = request.GET.get('welcome') == '1'

    context = {
        'eventos_hoy': eventos_hoy,
        'eventos_manana': eventos_manana,
        'eventos_encurso': eventos_encurso,
        'eventos_finalizados_hoy': eventos_finalizados_hoy,
        'show_welcome': show_welcome,
    }
    return render(request, 'eventos/dashboard.html', context)

@login_required
@user_passes_test(es_admin)
def estadisticas(request):
    hoy = timezone.localdate()
    
    # Datos para gráfico de la semana
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    eventos_semana = Evento.objects.filter(
        fecha_hora__date__range=[inicio_semana, fin_semana]
    )
    
    # Contar eventos por día de la semana
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    eventos_por_dia = [0] * 7
    
    for evento in eventos_semana:
        dia_semana = evento.fecha_hora.weekday()
        eventos_por_dia[dia_semana] += 1
    
    # Contar eventos por estado
    estados_count = {
        'programado': eventos_semana.filter(estado='programado').count(),
        'activo': eventos_semana.filter(estado='activo').count(),
        'finalizado': eventos_semana.filter(estado='finalizado').count(),
        'cancelado': eventos_semana.filter(estado='cancelado').count(),
    }
    
    # Eventos por sala
    from django.db.models import Count
    eventos_por_sala = list(Evento.objects.filter(
        fecha_hora__date__range=[inicio_semana, fin_semana]
    ).values('sala__nombre').annotate(total=Count('id')).order_by('-total'))

    context = {
        'dias_semana': dias_semana,
        'eventos_por_dia': eventos_por_dia,
        'estados_count': estados_count,
        'eventos_por_sala': eventos_por_sala,
        'total_eventos_semana': eventos_semana.count(),
    }
    return render(request, 'eventos/estadisticas.html', context)




@login_required
@user_passes_test(es_gestor_o_admin)
def crear_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.creado_por = request.user
            evento.save()
            if es_admin(request.user):
                return redirect('dashboard')
            else:
                return redirect('calendario') # Este ya estaba bien, pero lo confirmo
    else:
        form = EventoForm()
    
    salas_disponibles = Sala.objects.filter(activa=True)
    context = {'form': form, 'salas_disponibles': salas_disponibles}
    
    return render(request, 'eventos/crear_evento.html', context)

@login_required
@user_passes_test(es_gestor_o_admin)
def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            if es_admin(request.user):
                return redirect('dashboard')
            else:
                return redirect('calendario') # Este también estaba bien
    else:
        form = EventoForm(instance=evento)
        
    salas_disponibles = Sala.objects.filter(activa=True) # Se mantiene para el formulario
    context = {
        'form': form, 
        'evento': evento,
        'salas_disponibles': salas_disponibles
    }
    return render(request, 'eventos/editar_evento.html', context)

@login_required
@user_passes_test(es_gestor_o_admin)
def calendario_eventos(request):
    import calendar
    from collections import defaultdict
    from datetime import date
    
    # Obtener mes y año de parámetros GET o usar actual
    hoy = timezone.localdate()
    try:
        año = int(request.GET.get('year') or hoy.year)
        mes = int(request.GET.get('month') or hoy.month)
    except (ValueError, TypeError):
        año = hoy.year
        mes = hoy.month
    
    # Crear calendario del mes
    cal = calendar.monthcalendar(año, mes)
    
    # Obtener eventos del mes
    eventos_mes = Evento.objects.filter(
        fecha_hora__year=año,
        fecha_hora__month=mes
    )
    
    # Agrupar eventos por día (convertir a zona horaria local)
    eventos_por_dia = defaultdict(list)
    for evento in eventos_mes:
        # Convertir a zona horaria local antes de obtener el día
        fecha_local = timezone.localtime(evento.fecha_hora)
        dia = fecha_local.day
        eventos_por_dia[dia].append(evento)
    
    # Nombres de meses en español
    nombres_meses = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    # Calcular mes anterior y siguiente
    if mes == 1:
        mes_anterior, año_anterior = 12, año - 1
    else:
        mes_anterior, año_anterior = mes - 1, año
        
    if mes == 12:
        mes_siguiente, año_siguiente = 1, año + 1
    else:
        mes_siguiente, año_siguiente = mes + 1, año
    
    context = {
        'calendario': cal,
        'eventos_por_dia': dict(eventos_por_dia),
        'mes_nombre': nombres_meses[mes],
        'mes': mes,
        'año': año,
        'hoy': hoy.day if hoy.month == mes and hoy.year == año else None,
        'mes_anterior': mes_anterior,
        'año_anterior': año_anterior,
        'mes_siguiente': mes_siguiente,
        'año_siguiente': año_siguiente,
        'es_mes_actual': mes == hoy.month and año == hoy.year,
    }
    return render(request, 'eventos/calendario.html', context)

@login_required
@user_passes_test(es_admin)
def finalizar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    evento.estado = 'finalizado'
    evento.save()
    return redirect('dashboard')

@login_required
@user_passes_test(es_admin)
def notas(request):
    notas = Nota.objects.filter(creado_por=request.user)
    return render(request, 'eventos/notas.html', {'notas': notas})

@login_required
@user_passes_test(es_admin)
def crear_nota(request):
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.creado_por = request.user
            nota.save()
            return redirect('notas')
    else:
        form = NotaForm()
    return render(request, 'eventos/crear_nota.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def editar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id, creado_por=request.user)
    if request.method == 'POST':
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect('notas')
    else:
        form = NotaForm(instance=nota)
    return render(request, 'eventos/editar_nota.html', {'form': form, 'nota': nota})

@login_required
@user_passes_test(es_admin)
def eliminar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id, creado_por=request.user)
    if request.method == 'POST':
        nota.delete()
        return redirect('notas')
    return render(request, 'eventos/eliminar_nota.html', {'nota': nota})

@login_required
@user_passes_test(es_admin)
def imprimir_eventos_manana(request):
    hoy = timezone.localdate()
    manana = hoy + timedelta(days=1)
    
    eventos_manana = Evento.objects.filter(
        fecha_hora__date=manana,
        estado='programado'
    ).order_by('fecha_hora')
    
    # Formatear fecha en español
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    dia_semana = dias_semana[manana.weekday()]
    dia = manana.day
    mes = meses[manana.month]
    año = manana.year
    fecha_español = f"{dia_semana}, {dia} de {mes} de {año}"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Eventos de Mañana - {manana.strftime('%d/%m/%Y')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f8fafc; }}
        h1 {{ color: #009885; text-align: center; margin-bottom: 10px; }}
        h2 {{ text-align: center; color: #666; margin-bottom: 30px; }}
        .cards-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
            color: white;
            position: relative;
            overflow: hidden;
        }}
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ffd700, #ff6b35, #e83e8c);
        }}
        .card-title {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 12px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .card-meta {{
            margin: 8px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .card-equipment {{
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }}
        .equipment-tag {{
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        .card-status {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            margin-top: 12px;
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
        }}
        .empty-message {{
            text-align: center;
            color: #8993a4;
            font-style: italic;
            padding: 40px;
            background: white;
            border-radius: 12px;
            border: 2px dashed #dfe1e6;
        }}
        @media print {{
            body {{ margin: 0; background: white; }}
            .no-print {{ display: none; }}
            .cards-container {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <h1>🌅 Eventos Programados para Mañana</h1>
    <h2>{fecha_español}</h2>
    
    <button class="no-print" onclick="window.print()" style="background: #009885; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; margin-bottom: 20px; font-weight: 600;">🖨️ Imprimir</button>
    
    <div class="cards-container">
"""
    
    if eventos_manana:
        for evento in eventos_manana:
            equipamiento_html = ""
            if evento.requiere_laptop or evento.requiere_proyector:
                equipamiento_html = '<div class="card-equipment">'
                if evento.requiere_laptop:
                    laptop_info = f"Laptop{' #' + evento.numero_laptop if evento.numero_laptop else ''}"
                    equipamiento_html += f'<span class="equipment-tag">💻 {laptop_info}</span>'
                if evento.requiere_proyector:
                    equipamiento_html += '<span class="equipment-tag">📽️ Proyector</span>'
                equipamiento_html += '</div>'
            
            observaciones_html = ""
            if evento.observaciones:
                observaciones_html = f'<div class="card-meta"><strong>Observaciones:</strong> {evento.observaciones}</div>'
            
            html_content += f"""
        <div class="card">
            <div class="card-title">{evento.nombre}</div>
            <div class="card-meta"><strong>Hora:</strong> {evento.fecha_hora.strftime('%H:%M')}</div>
            <div class="card-meta"><strong>Sala:</strong> {evento.sala.nombre}</div>
            {observaciones_html}
            {equipamiento_html}
            <span class="card-status">Programado</span>
        </div>
"""
    else:
        html_content += '<div class="empty-message">No hay eventos programados para mañana</div>'
    
    html_content += """
    </div>
    <script>
        window.onload = function() {
            setTimeout(function() {
                window.print();
            }, 500);
        };
    </script>
</body>
</html>
"""
    
    return HttpResponse(html_content, content_type='text/html')
