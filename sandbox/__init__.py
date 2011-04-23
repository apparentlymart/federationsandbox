
from dfp import DFPHelper
from sandbox import settings
import logging

dfp_helper = DFPHelper(local_domain=settings.LOCAL_DOMAIN, override_domains=settings.OVERRIDE_DOMAINS, assoc_secret=settings.ASSOC_SECRET)

