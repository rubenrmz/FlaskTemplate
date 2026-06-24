# Autenticación

La autenticación es **opcional** y se controla con dos variables. Las rutas usan
siempre los mismos decoradores; el `.env` decide qué estrategia corre por debajo.

## Selector global

```bash
AUTH_REQUIRED=false      # true = la API exige auth; false = endpoints abiertos
AUTH_MODE=gateway        # gateway | jwt | jwt_pubkey  (solo aplica si AUTH_REQUIRED=true)
JWT_ROLES_CLAIM=roles    # nombre del claim con los roles (interop con emisores externos)
```

- Con `AUTH_REQUIRED=false`, `@require_auth` y `@require_roles(...)` se vuelven **no-op**
  (la ruta queda abierta). Útil para microservicios internos o APIs públicas.
- `Config.validate()` aborta el arranque si habilitas un modo sin su secreto/llave.

## Uso en las rutas

Siempre igual, sin importar el modo activo:

```python
from src.middleware.auth import require_auth, require_roles, get_current_user

@bp.route('/perfil')
@require_auth
def perfil():
    user = get_current_user()        # {"id": ..., "roles": [...], "email": ...} | None
    return jsonify(user)

@bp.route('/admin')
@require_roles('admin')              # exige al menos uno de los roles dados → 403 si no
def admin():
    ...
```

La identidad autenticada vive en `flask.g.current_user` y se obtiene con
`get_current_user()`. Su forma es siempre la misma en los tres modos:

```python
{"id": "<sub>", "roles": ["admin", ...], "email": "..."}
```

---

## Los 3 modos

| Modo | Quién valida el token | La app… | Cuándo usarlo |
|---|---|---|---|
| `gateway` | nginx/openresty (edge) | confía en headers inyectados | El proxy valida e inyecta la identidad (recomendado tras OpenResty) |
| `jwt` | la app (HS256, simétrico) | emite y verifica | App standalone con su propio login |
| `jwt_pubkey` | la app (RS/ES/EdDSA) | solo verifica con llave pública | Auth centralizada: un servicio firma, N servicios verifican |

### Modo `gateway` — identidad inyectada en el edge

El proxy valida el JWT (con su caché) e inyecta la identidad como headers. La app
**no revalida el JWT**: confía en los headers **solo si** el secreto compartido coincide
(comparación en tiempo constante con `hmac.compare_digest`). Fail-closed.

```bash
AUTH_REQUIRED=true
AUTH_MODE=gateway
GATEWAY_SHARED_SECRET=          # obligatorio. Generar: python -c "import secrets; print(secrets.token_hex(32))"
GATEWAY_SECRET_HEADER=X-Gateway-Secret
GATEWAY_HEADER_USER_ID=X-User-Id
GATEWAY_HEADER_ROLES=X-User-Roles
GATEWAY_HEADER_EMAIL=X-User-Email
```

**Seguridad — 3 capas (las dos primeras son responsabilidad del despliegue):**

1. **Aislamiento de red.** Gunicorn bindea `127.0.0.1`: la app nunca es accesible
   salvo a través del proxy. No expongas el puerto.
2. **El proxy debe SOBRESCRIBIR los headers de identidad del cliente**, no pasarlos.
   Esta es la línea crítica contra el spoofing.
3. **Secreto compartido** (lo aplica la app): si `X-Gateway-Secret` no coincide, se
   ignora la identidad y se responde 401.

Ejemplo de `location` en OpenResty (validación Lua + strip + secreto):

```nginx
location /api/ {
    access_by_lua_block {
        local jwt   = require "resty.jwt"
        local token = (ngx.var.http_authorization or ""):gsub("Bearer ", "")
        local v = jwt:verify("TU_SECRETO_JWT", token)
        if not v.verified then ngx.exit(401) end
        ngx.var.jwt_user  = v.payload.sub
        ngx.var.jwt_roles = table.concat(v.payload.roles or {}, ",")
    }
    # IMPORTANTE: sobrescribe (descarta) lo que mande el cliente
    proxy_set_header X-User-Id        $jwt_user;
    proxy_set_header X-User-Roles     $jwt_roles;
    proxy_set_header X-User-Email     "";
    proxy_set_header X-Gateway-Secret "EL_MISMO_GATEWAY_SHARED_SECRET";
    proxy_pass http://127.0.0.1:5000;
}
```

> **Nota sobre HMAC del request:** el secreto estático es la elección correcta para
> esta topología (proxy único y controlado). Un upgrade opcional sería firmar
> `método+path+timestamp` con HMAC para que el header no sea replayable. Solo vale la
> pena si la app deja de estar tras un único proxy de confianza (otro balanceador, una
> zona de menor confianza). Mientras sea OpenResty → Flask en infra controlada, no aporta.

### Modo `jwt` — login simétrico (HS256) dentro de la app

La app emite y verifica tokens con un secreto compartido. Expone endpoints de login.

```bash
AUTH_REQUIRED=true
AUTH_MODE=jwt
JWT_SECRET_KEY=                  # generar con secrets.token_hex(32); si vacío cae a SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRES=3600    # segundos
JWT_REFRESH_TOKEN_EXPIRES=2592000
```

- Requiere descomentar `PyJWT` en [`requirements.txt`](../requirements.txt).
- Se registran (solo en este modo) los endpoints:
  - `POST /auth/login` → `{username, password}` → `{access_token, refresh_token}`
  - `POST /auth/refresh` → `{refresh_token}` → `{access_token}`
  - Ambos están bajo `RATE_LIMIT_LOGIN` (ver [rate limiting](configuration.md#rate-limiting)).
- **Debes implementar `verify_credentials()`** en
  [src/api/auth_routes.py](../src/api/auth_routes.py) contra tu store de usuarios
  (hay un ejemplo con `check_password_hash` en el docstring). Mientras no lo hagas, el
  login responde 401.
- El cliente envía `Authorization: Bearer <access_token>` en cada request.

### Modo `jwt_pubkey` — verificación asimétrica (verify-only)

Un servicio centralizado (p. ej. un auth server en Rust) firma con su llave **privada**;
la app solo tiene la **pública** y verifica. No hay login aquí: la app no puede emitir.

```bash
AUTH_REQUIRED=true
AUTH_MODE=jwt_pubkey
JWT_PUBLIC_KEY=                  # PEM inline (con \n escapados) ...
JWT_PUBLIC_KEY_PATH=            # ... o ruta a un archivo .pem
JWT_ALGORITHM=RS256             # RS256 | ES256 | EdDSA | PS256 — debe coincidir con el emisor
JWT_ISSUER=                     # opcional: valida el claim 'iss'
JWT_AUDIENCE=                   # opcional: valida el claim 'aud'
```

- Requiere `PyJWT[crypto]` (incluye `cryptography`) en
  [`requirements.txt`](../requirements.txt).
- El cliente envía `Authorization: Bearer <token firmado por el servicio central>`.
- **Protección contra "algorithm confusion":** se fija `algorithms=[JWT_ALGORITHM]`,
  así un token firmado con HS256 (usando la pública como secreto) es rechazado.
- Si el emisor pone los roles en otro claim (ej. `permissions`), ajústalo con
  `JWT_ROLES_CLAIM`.

#### ¿`gateway` o `jwt_pubkey` con una auth centralizada?

Ambos sirven con un auth server central, pero resuelven cosas distintas:

- Si **OpenResty valida el token e inyecta headers** → usa `gateway`. La app no toca el JWT.
- Si quieres que **Flask verifique el token por sí mismo** (defensa en profundidad, o
  cuando el proxy solo hace passthrough del `Authorization`) → usa `jwt_pubkey`.

---

## Decoradores específicos por estrategia

Además del selector unificado, cada estrategia expone decoradores que la fuerzan sin
importar `AUTH_MODE` (útil para un endpoint puntual):

- `from src.middleware.gateway_auth import require_gateway_identity, require_gateway_roles`
- `from src.middleware.jwt_auth import require_jwt`
- `from src.middleware.pubkey_auth import require_pubkey_jwt`

En general, prefiere `require_auth` / `require_roles` de
[src/middleware/auth.py](../src/middleware/auth.py) para que el `.env` mande.

## Llave de admin (independiente del modo)

`@require_admin_key` ([src/middleware/key_auth.py](../src/middleware/key_auth.py))
protege endpoints de administración con el header `X-Admin-Key` contra `ADMIN_SECRET_KEY`
(comparación en tiempo constante). Es independiente de `AUTH_MODE`; se usa, por ejemplo,
en el healthcheck de base de datos.
