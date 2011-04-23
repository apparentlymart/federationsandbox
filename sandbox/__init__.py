
from dfp import DFPHelper
from sandbox import settings
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import logging

dfp_helper = DFPHelper(local_domain=settings.LOCAL_DOMAIN, override_domains=settings.OVERRIDE_DOMAINS, assoc_secret=settings.ASSOC_SECRET)

template_dir = os.path.dirname(__file__) + "/../templates"

def render_template(fn, vars):
    full_path = os.path.join(template_dir, fn)
    vars["remote_user"] = users.get_current_user()
    vars["login_url"] = "/mine"
    vars["logout_url"] = users.create_logout_url("/");
    return template.render(full_path, vars)

def print_template(fn, vars):
    print render_template(fn, vars)

def remote_user():
    return users.get_current_user()

