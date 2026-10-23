# Pruebas y verificación

Verificación realizada para la edición pública de CardG API.

## Entorno

| Elemento | Valor |
| --- | --- |
| Sistema | Windows |
| Python | 3.12.10 |
| Django | 5.2.18 |
| Django REST Framework | 3.18.3 |
| Base de datos de pruebas | SQLite |

## Comandos

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py seed_demo --reset
python manage.py test
python manage.py spectacular --file schema.yaml --validate
python manage.py collectstatic --noinput --clear
```

## Resultados

| Verificación | Resultado |
| --- | --- |
| `manage.py check` | Sin errores. |
| `makemigrations --check` | No hay cambios pendientes. |
| Migraciones | Aplicadas correctamente. |
| `seed_demo --reset` | 6 categorías, 10 productos, 8 mesas, 6 pedidos, 4 pagos y 3 usuarios. |
| Suite de pruebas | 60 pruebas aprobadas. |
| Cobertura medida | 98% de líneas con el comando de cobertura indicado abajo. |
| Esquema OpenAPI | Generado y validado sin errores. |
| Archivos estáticos | 169 archivos recolectados; 158 posprocesados. |

## Cobertura

```powershell
python -m coverage run --source=categories,core,icard,orders,payments,products,tables,users manage.py test --verbosity 0
python -m coverage report -m
```

La cifra incluye archivos de prueba y migraciones. El objetivo es detectar rutas sin ejercitar, no presentar una métrica de producción.

## Pruebas manuales de humo

| Petición | Resultado |
| --- | --- |
| `GET /` | 200, panel de demostración. |
| `GET /api/health/` | 200, `status=ok`, `database=ok`. |
| `GET /api/schema/` | 200, OpenAPI 3. |
| `GET /docs/` | 200, Swagger UI con recursos locales. |
| `POST /api/auth/login/` | 200, access y refresh tokens. |
| `POST /api/auth/refresh/` | 200, nuevo access token. |
| `GET /api/auth/me/` | 200, perfil sin contraseña. |
| `GET /api/products/?active=true` | 200, 9 productos activos. |
| `GET /api/orders/` | 200, 6 pedidos. |
| `POST /api/orders/` sin token | 401. |

## Notas

- Las pruebas crean bases de datos temporales y archivos de imagen temporales; no tocan los datos de demostración locales.
- `check --deploy` muestra advertencias esperadas cuando se usa la configuración de desarrollo (`DEBUG=1` y clave de demostración). En producción deben configurarse las variables descritas en el README.
- El comando `seed_demo --reset` es destructivo para los datos de las apps de la carta. Está pensado exclusivamente para la demo.
