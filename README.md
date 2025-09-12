# Sistema de Gestión de Eventos y Salas

Sistema web desarrollado en Django para la gestión de eventos y reserva de salas con equipamiento.

## Características

- 📅 Dashboard con vista de eventos por columnas (En curso, Hoy, Finalizados, Mañana)
- 🏢 Gestión de salas y equipamiento (laptops, proyectores)
- 📝 Sistema de notas con colores
- 📊 Estadísticas de uso
- 🖨️ Impresión de eventos
- 🔄 Actualización automática del dashboard

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/maquio369/Gestion-de-salas.git
cd Gestion-de-salas
```

2. Crea un entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
```

3. Instala las dependencias:
```bash
pip install django django-crispy-forms crispy-bootstrap5
```

4. Ejecuta las migraciones:
```bash
python manage.py migrate
```

5. Crea un superusuario:
```bash
python manage.py createsuperuser
```

6. Ejecuta el servidor:
```bash
python manage.py runserver
```

## Uso

- Accede a `http://127.0.0.1:8000/` para ver el dashboard
- Usa el panel de administración en `/admin/` para gestionar salas y equipos
- Crea eventos desde el dashboard con el botón "Nuevo Evento"

## Tecnologías

- Django 4.x
- SQLite (Base de datos por defecto en este proyecto)
- HTML/CSS/JavaScript
- Bootstrap (opcional)

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request