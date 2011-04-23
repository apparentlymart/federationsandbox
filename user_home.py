
from google.appengine.api import users
from google.appengine.ext import db
from os import environ
import cgi
import sandbox

user = sandbox.remote_user()

if environ["REQUEST_METHOD"] != "POST":

    entities_owned = sandbox.Entity.get_by_user(user)

    sandbox.template_response("user_home.html", {"entities_owned": entities_owned})

else:

    fields = cgi.FieldStorage()
    mode = fields["mode"].value

    if mode == "create_entity":
        import uuid
        name = uuid.uuid4().hex
        entity = sandbox.Entity(name=name)
        entity.put()

    sandbox.redirect("/mine")
