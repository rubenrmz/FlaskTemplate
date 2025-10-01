import ssl
import requests
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class TLSAdapter(HTTPAdapter):
    """
    Adapter para bajar SECLEVEL a 1 y permitir ciphers viejos
    Compatible con gevent
    """
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)

_session = None

def get_session():
    """
    Retorna una sesión HTTP reutilizable con:
    - TLS personalizado (SECLEVEL=1)
    - Pool de conexiones
    - Compatible con gevent
    """
    global _session
    
    if _session is None:
        _session = requests.Session()
        
        retry_strategy = Retry(
            total=0,  # Sin reintentos automáticos
            backoff_factor=0,
            status_forcelist=[],
            allowed_methods=[]
        )
        
        # Crear adapter con TLS personalizado y reintentos
        adapter = TLSAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        _session.mount("https://", adapter)
        _session.mount("http://", HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        ))
    
    return _session