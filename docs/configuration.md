# Configuración general

Todo se controla por variables de entorno. Plantilla completa en
[`.env.example`](../.env.example); los defaults viven en
[src/config/settings.py](../src/config/settings.py).

Para autenticación, ver [auth.md](auth.md).

## Índice

- [Flask y entorno](#flask-y-entorno)
- [Seguridad HTTP](#seguridad-http)
- [CORS](#cors)
- [Rate limiting](#rate-limiting)
- [Base de datos](#base-de-datos)
- [Mail](#mail)
- [Redis](#redis)
- [WebSockets](#websockets)
- [Logging](#logging)
- [Gunicorn](#gunicorn)

---

## Flask y entorno

```bash
FLASK_ENV=development         # production | development | testing
FLASK_PORT=5000
APP_NAME=flask_app
SECRET_KEY=                   # firma cookies/sesiones — obligatorio cambiarlo en prod
ADMIN_SECRET_KEY=             # header X-Admin-Key para endpoints admin — obligatorio en prod
APP_TIMEZONE=America/Mexico_City
API_PREFIX=/api/v1            # prefijo de todos los blueprints
IS_DEV=false                  # bandera global para alternar lógica dev/prod en rutas
```

`FLASK_ENV=production` activa el modo estricto de `Config.validate()` y cambia el
comportamiento de logging (archivo en vez de consola) y de las cookies (`Secure`).

## Seguridad HTTP

Headers aplicados a toda respuesta por
[src/config/security.py](../src/config/security.py): `X-Frame-Options: DENY`,
`X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Content-Security-Policy:
default-src 'self'`, `Permissions-Policy`. En producción se añade `Strict-Transport-Security`.

```bash
MAX_CONTENT_LENGTH_MB=16      # tamaño máximo del body (anti-DoS)
SESSION_COOKIE_SAMESITE=Lax   # Lax | Strict | None
TRUSTED_PROXY_COUNT=0         # nº de proxies de confianza al frente (nginx/openresty)
```

- Las cookies de sesión son `HttpOnly` siempre y `Secure` en producción.
- **`TRUSTED_PROXY_COUNT`**: con `0` no se aplica `ProxyFix` (evita spoofing de
  `X-Forwarded-For`). Detrás de un único nginx/openresty, ponlo en `1` para que el rate
  limiting y los logs vean la IP real del cliente, no la del proxy.

## CORS

[src/config/cors.py](../src/config/cors.py). Aplica a todas las rutas (`/*`).

```bash
CORS_ORIGINS=http://localhost:3000   # orígenes permitidos, separados por coma
CORS_METHODS=GET,POST,PUT,DELETE     # OPTIONS se añade siempre de forma automática
CORS_MAX_AGE=3600                    # cacheo del preflight (seg). Dev: 60 | Prod: 3600
```

- `allow_headers` está fijo en `Content-Type, Authorization`; `supports_credentials=True`.
- **Producción:** `Config.validate()` rechaza `CORS_ORIGINS=*` o el default
  `http://localhost:3000`. Define tus dominios reales:
  `CORS_ORIGINS=https://tudominio.com,https://admin.tudominio.com`.

## Rate limiting

[Flask-Limiter](https://flask-limiter.readthedocs.io), key por IP remota.

```bash
RATE_LIMIT_DEFAULT=100 per hour   # límite global por cliente
RATE_LIMIT_LOGIN=5 per minute     # aplicado a /auth/login y /auth/refresh (modo jwt)
```

- El **storage** es el de Redis si `REDIS_ENABLED=true`, o `memory://` si no. Con varios
  workers de Gunicorn, `memory://` cuenta por-proceso: para un límite global real usa Redis.
- Detrás de un proxy, configura `TRUSTED_PROXY_COUNT` o el límite se aplicará a la IP del
  proxy (es decir, global) en vez de por cliente.
- Para limitar una ruta específica: `@limiter.limit("10 per minute")`
  (importa `limiter` de [src/config/extensions.py](../src/config/extensions.py)).

## Base de datos

Opcional, con dos modos excluyentes. `ORM_ENABLED=true` requiere `DB_ENABLED=true`.

```bash
DB_ENABLED=false
ORM_ENABLED=false             # false = PyMySQL directo (Modo A) | true = SQLAlchemy (Modo B)
DB_TYPE=mysql                 # mysql | postgresql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=test
DB_USER=root
DB_PASSWORD=
```

### Modo A — PyMySQL directo (`ORM_ENABLED=false`)

Queries simples sin ORM. Descomenta `PyMySQL` (o `psycopg2-binary`) en
[`requirements.txt`](../requirements.txt). Expone en
[src/config/extensions.py](../src/config/extensions.py):

```python
from src.config.extensions import get_connection, get_db, check_db_connection

with get_db() as conn:                       # context manager, cierra al salir
    cur = conn.cursor()
    cur.execute("SELECT %s", (1,))           # SIEMPRE parametrizado (anti-inyección)
    rows = cur.fetchall()
```

### Modo B — SQLAlchemy + marshmallow (`ORM_ENABLED=true`)

Modelos con relaciones y serialización. Descomenta `Flask-SQLAlchemy`,
`Flask-Marshmallow`, `marshmallow-sqlalchemy` y el driver. Expone `db` (con `Base`
declarativa) y `ma`. La URI se construye automáticamente desde las variables `DB_*`.

## Mail

Opcional, vía [Flask-Mailman](https://flask-mailman.readthedocs.io). Descomenta
`Flask-Mailman` en [`requirements.txt`](../requirements.txt).

```bash
MAIL_ENABLED=false
MAIL_SERVER=
MAIL_PORT=
MAIL_USE_TLS=                 # Prod: True
MAIL_USE_SSL=
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=          # email verificado en tu proveedor
MAIL_TIMEOUT=                 # Prod: 30-60
MAIL_MAX_EMAILS=
MAIL_ASCII_ATTACHMENTS=
```

## Redis

Opcional sin WebSockets (caché o rate limiting distribuido); **obligatorio** con
WebSockets (como message broker). Connection pool en
[src/config/extensions.py](../src/config/extensions.py).

```bash
REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

## WebSockets

Opcional, vía [Flask-SocketIO](https://flask-socketio.readthedocs.io) + gevent.
**Requiere `REDIS_ENABLED=true`** como broker.

```bash
WS_ENABLED=false
```

Checklist al habilitar:

1. En [`requirements.txt`](../requirements.txt): descomenta `gevent`,
   `flask-socketio`, `simple-websocket`.
2. `GUNICORN_WORKER_CLASS=gevent` y `GUNICORN_WORKERS=1`.
3. `REDIS_ENABLED=true`.
4. El arranque usa [`wsgi.py`](../wsgi.py) (hace `monkey.patch_all()` **antes** de todo).
   [`start.sh`](../start.sh) detecta `WS_ENABLED=true` y arranca con `wsgi:app`.

Los eventos se registran en
[src/api/socket_events.py](../src/api/socket_events.py). El CORS del handshake usa
`CORS_ORIGINS` (la misma allowlist que el resto de la API).

## Logging

[src/config/logging.py](../src/config/logging.py).

```bash
LOG_LEVEL=INFO                # DEBUG | INFO | WARNING | ERROR | CRITICAL
```

- **Producción:** `RotatingFileHandler` en `logs/app.log` (10 MB × 5 archivos, evita
  llenar disco).
- **Desarrollo:** salida por consola.

## Gunicorn

Configuración completa en [`gunicorn.conf.py`](../gunicorn.conf.py); todos los valores
salen de variables de entorno. Resumen de las que más se tocan:

```bash
GUNICORN_WORKERS=3                 # (CPU*2)+1 sin WS; 1 con WS (gevent)
GUNICORN_WORKER_CLASS=gthread      # sync | gthread | gevent
GUNICORN_THREADS=4                 # solo gthread
GUNICORN_WORKER_MAX_CONNECTIONS=1000  # solo gevent
GUNICORN_TIMEOUT=30
GUNICORN_GRACEFUL_TIMEOUT=30
GUNICORN_KEEP_ALIVE=5              # menor que el de nginx si hay proxy
GUNICORN_MAX_REQUESTS=1000         # recicla workers (anti memory leak)
GUNICORN_MAX_REQUESTS_JITTER=100
GUNICORN_DAEMON=false              # false para systemd
```

- Bindea `127.0.0.1:FLASK_PORT`. Detrás de nginx/openresty, deja el bind local y
  configura `TRUSTED_PROXY_COUNT`. En producción se recomienda socket unix.
- Arranque: `./start.sh` (elige `gthread` o `gevent`/`wsgi:app` según `WS_ENABLED`).
