
from dfp import DFPHelper
from sandbox import settings


dfp_helper = DFPHelper(local_domain="localhost", override_domains=settings.OVERRIDE_DOMAINS, assoc_secret=settings.ASSOC_SECRET)


