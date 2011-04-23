
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


class SubscriptionFromRemoteEntity(db.Model):
    local_entity = db.ReferenceProperty(reference_class=Entity,
                                        required=True,
                                        collection_name="subscriptions_from_remote_entities")
    remote_entity_name = db.StringProperty(required=True)
    remote_entity_domain = db.StringProperty(required=True)


class SocialMessageReceived(db.Model):
    local_entity = db.ReferenceProperty(reference_class=Entity,
                                        required=True,
                                        collection_name="messages_received")
    remote_entity_name = db.StringProperty(required=True)
    remote_entity_domain = db.StringProperty(required=True)
    type = db.StringProperty(required=True)
    payload = db.TextProperty()

