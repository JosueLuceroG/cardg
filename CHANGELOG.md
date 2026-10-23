# Changelog

Todas las fechas usan el formato AAAA-MM-DD.

## [2.0.0] - 2026-10-23

### Añadido

- Edición pública de portafolio con datos ficticios.
- App `core` y comando `seed_demo` para crear categorías, productos, mesas, pedidos, pagos y usuarios de demostración.
- Imágenes sanitizadas en `demo_assets/`, sin EXIF ni datos personales.
- Documentación interactiva con drf-spectacular: `/docs/`, `/redoc/` y `/api/schema/`.
- Endpoints `/api/health/` y `/api/` con el resumen de la API.
- Página de presentación en `/` con el estado de la demo.
- Suite de 60 pruebas de API, autenticación, permisos, filtros y datos ficticios.
- Configuración por variables de entorno, CORS, JWT y WhiteNoise.
- `README.md`, `TESTING.md`, `CHANGELOG.md`, `.env.example` y `Procfile`.

### Cambiado

- Django actualizado de 3.2.7 a 5.2.18.
- Django REST Framework actualizado a 3.18.3.
- Autenticación JWT con SimpleJWT: 60 minutos para access y 1 día para refresh.
- Inicio de sesión por correo electrónico.
- Los usuarios se crean con username automático y contraseña hasheada mediante `set_password`.
- Lectura pública de la carta y escritura autenticada; usuarios solo para administradores.
- Migración de `drf_yasg` a drf-spectacular.
- Plantilla principal movida a `templates/icard/home.html`.

### Corregido

- Eliminada la `SECRET_KEY` hardcodeada de los settings.
- Eliminado `ALLOWED_HOSTS` específico de un despliegue anterior.
- El serializer de usuarios ya no expone la contraseña.
- Corregida la relación opcional entre pagos y mesas.
- Eliminados del repositorio la base de datos real, uploads, `.DS_Store`, `__pycache__` y archivos `.pyc`.

### Seguridad

- No se publican correos, contraseñas, hashes ni archivos de usuarios reales.
- Las credenciales de demostración son únicamente locales.
- La configuración de producción requiere `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, hosts, CORS y CSRF explícitos.

### Compatibilidad

- Requiere Python 3.12 o superior.
- El login ahora usa `email` en lugar de `username`.
- La API pública permite lectura sin autenticación; las operaciones de escritura requieren JWT.
- El comando de datos de demostración vive en `core`, no en `icard`.
