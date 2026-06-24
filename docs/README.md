# Documentación

Guía de configuración y operación del template Flask. Toda la configuración se
controla por variables de entorno (ver [`.env.example`](../.env.example)).

## Índice

- **[auth.md](auth.md)** — Autenticación: selector global, los 3 modos
  (`gateway` / `jwt` / `jwt_pubkey`), decoradores, identidad y consideraciones de seguridad.
- **[configuration.md](configuration.md)** — Configuración general de operación:
  CORS, rate limiting, base de datos (ORM / PyMySQL), mail, Redis, WebSockets,
  logging, headers de seguridad y Gunicorn.

## Mapa rápido

| Necesito… | Sección |
|---|---|
| Proteger endpoints | [auth.md](auth.md) |
| Permitir un frontend (origen) | [CORS](configuration.md#cors) |
| Limitar requests por cliente | [Rate limiting](configuration.md#rate-limiting) |
| Conectar una base de datos | [Base de datos](configuration.md#base-de-datos) |
| Enviar correos | [Mail](configuration.md#mail) |
| WebSockets en tiempo real | [WebSockets](configuration.md#websockets) |
| Caché / broker | [Redis](configuration.md#redis) |
| Ajustar workers / despliegue | [Gunicorn](configuration.md#gunicorn) |

## Requisito de versión

El template exige **Python 3.14+**. Se valida en tres capas:
[`.python-version`](../.python-version) (pyenv), un guard en
[`start.sh`](../start.sh), y `Config.validate()` al arrancar la app.

## Validación al arrancar

`Config.validate()` ([src/config/settings.py](../src/config/settings.py)) aborta el
arranque si la configuración es incoherente. En **producción** (`FLASK_ENV=production`)
es estricto: exige cambiar `SECRET_KEY` y `ADMIN_SECRET_KEY`, no permite `CORS_ORIGINS`
por defecto/`*`, y exige `REDIS_ENABLED=true` si `WS_ENABLED=true`. Si habilitas auth,
exige el secreto/llave del modo elegido.
