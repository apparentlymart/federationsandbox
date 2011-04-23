
from google.appengine.api import users
import sandbox
import cgi
from os import environ

if environ["REQUEST_METHOD"] != "POST":
    print "Content-type: text/html\n\n"
    sandbox.print_template("login.html", {})
else:
    fields = cgi.FieldStorage()
    id = fields["id"]
    url = users.create_login_url(federated_identity=id.value,
                                 dest_url="/mine")
    print "Status: 302 Moved"
    print "Location: " + url
    print "Content-Type: text/html\n"


