
import urllib
import urllib2
import re
import logging
import hashlib
import hmac
from time import time

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

    def __init__(self, local_domain=None, override_domains=None, assoc_secret=None):
        self.local_domain = local_domain
        self.override_domains = override_domains if override_domains else {}
        self.assoc_secret = assoc_secret

        if self.local_domain is None:
            raise ValueError("local_domain must be specified")
        if self.assoc_secret is None:
            raise ValueError("assoc_secret must be specified")

        log.debug("Created DFPHelper for domain %s with override_domains %r", local_domain, override_domains)

    def discovery_url_for_domain(self, domain):
        if not re.match("^[a-zA-Z0-9\-]+(.[a-zA-Z0-9\-]+)*$", domain):
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

    def request_association_for_domain(self, domain):
        endpoint = self.associate_endpoint_for_domain(domain)
        verifier = self.make_token("v", domain)

        fields = {
            "mode": "associate",
            "domain": self.local_domain,
            "verifier": verifier
        }
        payload = urllib.urlencode(fields)
        response = urllib2.urlopen(endpoint, payload)

        data = json.load(response)
        return data

    def verify_incoming_association_request(self, domain, verifier):
        endpoint = self.associate_endpoint_for_domain(domain)

        fields = {
            "mode": "verify",
            "domain": self.local_domain,
            "verifier": verifier
        }
        payload = urllib.urlencode(fields)
        log.debug("Issuing verify request for %r to %r", domain, endpoint)
        try:
            response = urllib2.urlopen(endpoint, payload)
        except urllib2.URLError, ex:
            log.error("Failed to make verification request for domain %r", domain)
            return False

        try:
            data = json.load(response)
        except ValueError, ex:
            log.error("Failed to parse verify response from domain %r", domain)
            return False

        if "verifier" in data and data["verifier"] == verifier:
            return True
        else:
            log.error("Domain %r did not echo back the verifier", domain)
            return False

    def verify_outgoing_association_request(self, domain, verifier):
        actual_domain = self.domain_for_token("v", verifier)
        if actual_domain == domain:
            return True
        else:
            log.error("No outgoing association request for domain %r matches %r; verifier represents %r", domain, verifier, actual_domain)
            return False

    def association_response_dict(self, domain):
        token = self.make_token("a", domain)
        return {
            "token": token,
            "expires_in": 3600,
        }

    def make_token(self, type, domain, ts=None):
        if ts is None:
            ts = time()
        
        parts = []
        parts.append(type)
        parts.append(domain)
        parts.append("%i" % ts)

        sig = self.make_signature(parts)
        parts.append(sig)
        return ":".join(parts)

    def make_signature(self, parts):
        base_string = ":".join(parts)
        log.debug("Signature base string is %r", base_string)

        mac = hmac.new(self.assoc_secret, base_string, hashlib.sha256)
        return mac.hexdigest()

    def domain_for_token(self, expected_type, token):
        parts = token.split(":", 3)

        try:
            type = parts[0]
            domain = parts[1]
            ts = parts[2]
            sig = parts[3]
        except IndexError:
            logging.error("Token is not in the expected format")
            return None

        current_ts = time()

        if expected_type != type:
            logging.error("Wrong type of token")
            return None

        if (current_ts - int(ts)) > 3720:
            logging.error("Token has expired")
            return None

        expected_sig = self.make_signature([ type, domain, ts ])

        # In a real implementation this should use
        # a constant-time comparison function, but
        # for the sandbox implementation this
        # is sufficient.
        if (sig != expected_sig):
            logging.error("Signature does not match (%r != %r)", sig, expected_sig)
            return None

        return domain
