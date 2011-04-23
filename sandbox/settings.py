
LOCAL_DOMAIN="federationsandbox.appspot.com"
ASSOC_SECRET = "not-so-secret-for-development"
OVERRIDE_DOMAINS = {}

try:
    from sandbox.local_settings import *
except ImportError, ex:
    # Oh well
    pass

