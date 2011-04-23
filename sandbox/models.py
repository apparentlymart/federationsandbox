
from google.appengine.ext import db
from google.appengine.api import users

class Entity(db.Model):
    name = db.StringProperty(required=True)
    latest_send_time = db.DateTimeProperty()
    latest_recv_time = db.DateTimeProperty()
    create_time = db.DateTimeProperty(auto_now_add=True)
    user = db.UserProperty(auto_current_user_add=True)

    @classmethod
    def get_by_user(cls, user):
        return db.GqlQuery("SELECT * FROM Entity WHERE user=:1 ORDER BY create_time", user)

