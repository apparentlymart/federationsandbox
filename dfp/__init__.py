
import urllib2
import re
import logging

log = logging.getLogger("dfp")

# Try three different ways to find the json library,
# depending on what environment we're running in.
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        # Google AppEngine only has django's bundled version
        from django.utils import simplejson as json

class DiscoveryError(Exception):
    pass

class DFPHelper(object):

    def __init__(self, local_domain=None, override_domains=None):
        self.local_domain = local_domain
        self.override_domains = override_domains if override_domains else {}

        if self.local_domain is None:
            raise ValueError("local_domain must be specified")

        log.debug("Created DFPHelper for domain %s with override_domains %r", local_domain, override_domains)

    def discovery_url_for_domain(self, domain):
        if not re.match("^(a-zA-Z0-9\-)(.(a-zA-Z0-9\-))*$", domain):
            raise ValueError("domain must be a valid, ASCII-only domain")

        return "https://" + domain + "/.well-known/federation"
    
    def discover(self, domain):

        # If the discovery info for this domain has been overridden
        # in the config, then just return that override.
        if domain in self.override_domains:
            log.debug("The domain %s is overridden in local config", domain)
            return self.override_domains[domain]

        url = self.discovery_url_for_domain(domain)
        log.debug("Fetching federation document for %s from %s", domain, url)

        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError, ex:
            raise DiscoveryError(ex)

        try:
            return json.load(response)
        except Exception, ex:
            raise DiscoveryError(ex)

    def associate_endpoint_for_domain(self, domain):
        disco = self.discover(domain)
        if "associate" in disco:
            log.debug("The domain %s handles associations at %s", domain, disco["associate"])
            return disco["associate"]
        else:
            log.debug("The domain %s does not declare an associate endpoint", domain)
            return None

