
from dfp import DFPHelper, json
from sandbox import settings
from google.appengine.ext.webapp import template
from google.appengine.api import users
from models import *
import os
import logging

dfp_helper = DFPHelper(local_domain=settings.LOCAL_DOMAIN, override_domains=settings.OVERRIDE_DOMAINS, assoc_secret=settings.ASSOC_SECRET)

template_dir = os.path.dirname(__file__) + "/../templates"

def print_header(status=200, content_type="text/html"):
    print "Status: %s Whatever" % status
    print "Content-Type: %s" % content_type
    print ""

def render_template(fn, vars):
    full_path = os.path.join(template_dir, fn)
    vars["remote_user"] = users.get_current_user()
    vars["login_url"] = "/mine"
    vars["logout_url"] = users.create_logout_url("/");
    vars["settings"] = settings
    return template.render(full_path, vars)

def print_template(fn, vars):
    print render_template(fn, vars)

def template_response(fn, vars):
    print_header()
    print_template(fn, vars)

def remote_user():
    return users.get_current_user()

def redirect(url):
    print "Status: 302 Found"
    print "Location: %s" % url
    print "Content-Type: text/html"
    print ""
    print "redirect"

def json_response(dict):
    print "Content-Type: application/json"
    print ""
    print json.dumps(dict)

