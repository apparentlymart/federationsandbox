
from google.appengine.api import users
import sandbox

user = users.get_current_user()

print "Content-type: text/html\n\n"

sandbox.print_template("page.html", {})


