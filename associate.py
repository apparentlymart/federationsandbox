
import cgi
import sandbox
import sys
from os import environ
from django.utils import simplejson as json
import logging


dfp_helper = sandbox.dfp_helper
fields = cgi.FieldStorage()


def associate(domain, verifier):

    if dfp_helper.verify_incoming_association_request(domain, verifier):
        response_dict = dfp_helper.association_response_dict(domain)
        print "Content-Type: application/json"
        print ""
        print json.dumps(response_dict)
    else:
        logging.error("Dialback verification failed for domain %r with verifier %r", domain, verifier)
        request_error("Request dialback verification failed")


def verify(domain, verifier):
    if dfp_helper.verify_outgoing_association_request(domain, verifier):
        print "Content-Type: application/json"
        print ""
        print json.dumps({"verifier": verifier})
    else:
        logging.error("Domain %r tried to verify with %r but that doesn't match a request we made", domain, verifier)
        request_error("Not a request I made")


def request_error(message, status_line="400 Bad Request"):
    print "Status: " + status_line
    print "Content-Type: text/html"
    print ""
    print cgi.escape(message)
    sys.exit(0)


if environ["REQUEST_METHOD"] != "POST":
    request_error("Must make a POST request", "405 Method Not Allowed")

try:
    domain = fields["domain"].value
    mode = fields["mode"].value
    verifier = fields["verifier"].value
except KeyError, ex:
    request_error("Missing required request parameter '%s'" % ex)

if mode == "associate":
    associate(domain, verifier)
elif mode == "verify":
    verify(domain, verifier)
else:
    request_error("Invalid mode '%s'" % mode);

