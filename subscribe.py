
import cgi
import sandbox
import dfp
import sys
from os import environ
from django.utils import simplejson as json
import logging


dfp_helper = sandbox.dfp_helper
fields = cgi.FieldStorage()


def subscribe(local_entity, remote_entity, remote_domain):
    logging.info("Subscription request for our %r from %r@%r", local_entity, remote_entity, remote_domain)


def unsubscribe(local_entity, remote_entity, remote_domain):
    logging.info("Unsubscription request for our %r from %r@%r", local_entity, remote_entity, remote_domain)


def request_error(message, status_line="400 Bad Request"):
    print "Status: " + status_line
    print "Content-Type: text/html"
    if status_line == "401 Unauthorized":
        print "WWW-Authenticate: DFPEntity"
    print ""
    print cgi.escape(message)
    sys.exit(0)


if environ["REQUEST_METHOD"] != "POST":
    request_error("Must make a POST request", "405 Method Not Allowed")

if "HTTP_AUTHORIZATION" not in environ:
    request_error("Must send Authorization: DFPEntity header", "401 Unauthorized")

try:
    mode = fields["mode"].value
    local_entity = fields["entity"].value
except KeyError, ex:
    request_error("Missing required request parameter '%s'" % ex)

auth_header = environ["HTTP_AUTHORIZATION"]
try:
    remote_entity, remote_domain = dfp_helper.identity_from_authorization_header(auth_header)
except dfp.AuthHeaderParseError:
    request_error("Malformed Authorization header")
except dfp.InvalidAssociationError:
    request_error("Association token is invalid", "401 Unauthorized")

if mode == "subscribe":
    subscribe(local_entity, remote_entity, remote_domain)
elif mode == "unsubscribe":
    unsubscribe(local_entity, remote_entity, remote_domain)
else:
    request_error("Invalid mode '%s'" % mode);

