
from google.appengine.api import users
from google.appengine.ext import db
from os import environ
import cgi
import sandbox
import re
import logging
import urllib
import urllib2
import dfp
from sandbox.models import *

user = sandbox.remote_user()
path_info = environ["PATH_INFO"]
match = re.search("([a-z0-9]+)$", path_info)
entity_id = match.group(1)
entity = Entity.get_by_name(entity_id)
owned = True if user == entity.user else False

if entity is None:
    print "Status: 404 Not Found"
    print "Content-Type: text/html"
    print ""
    print "no such entity"
    exit()


if environ["REQUEST_METHOD"] != "POST":

    #entities_owned = sandbox.Entity.get_by_user(user)

    messages = entity.messages_received.order("-receive_time").fetch(20)
    subscriptions = entity.subscriptions_from_remote_entities.order("-create_time").fetch(10)

    sandbox.template_response("entity_home.html", {"entity": entity,
                                                   "messages": messages,
                                                   "subscriptions": subscriptions,
                                                   "owned": owned})

elif owned:

    fields = cgi.FieldStorage()
    mode = fields["mode"].value

    if mode == "subscribe":
        remote_entity = fields["entity"].value
        remote_domain = fields["domain"].value
        disco_doc = sandbox.dfp_helper.discover(remote_domain)
        if disco_doc is None or "subscribe" not in disco_doc:
            logging.debug("The domain %r doesn't declare a subscribe endpoint", remote_domain)
            sandbox.template_response("entity_home_subscribe_fail.html", {})
            exit()
        subscribe_endpoint = disco_doc["subscribe"]
        logging.debug("The domain %r accepts subscription requests at %r", remote_domain, subscribe_endpoint)
        assoc_dict = sandbox.dfp_helper.request_association_for_domain(remote_domain)
        if assoc_dict is None or "token" not in assoc_dict:
            logging.debug("Failed to get association for domain %r", remote_domain)
            sandbox.template_response("entity_home_subscribe_fail.html", {})
            exit()
        assoc_token = assoc_dict["token"]
        logging.debug("Going to do a subscription request for domain %r to endpoint %r using association token %r", remote_domain, subscribe_endpoint, assoc_token)
        fields = {
            "mode": "subscribe",
            "entity": remote_entity,
        }
        payload = urllib.urlencode(fields)
        request = urllib2.Request(subscribe_endpoint, payload, {"Authorization": "DFPEntity "+entity.name+" "+assoc_token})
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, ex:
            logging.error("Failed to make subscription request for domain %r", remote_domain)
            sandbox.template_response("entity_home_subscribe_fail.html", {})
            exit()

        try:
            data = dfp.json.load(response)
        except ValueError, ex:
            logging.error("Failed to parse subscription response from domain %r", remote_domain)
            sandbox.template_response("entity_home_subscribe_fail.html", {})
            exit()

        logging.info("Subscription request for entity %r at domain %r from local entity %r succeeded and returned %r", remote_entity, remote_domain, entity.name, data)


    sandbox.redirect(environ["PATH_INFO"])


