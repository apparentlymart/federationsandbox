
from google.appengine.api import users
from os import environ
import cgi
import sandbox
import logging
import dfp
import urllib2

user = sandbox.remote_user()

if environ["REQUEST_METHOD"] != "POST":

    sandbox.template_response("try_associate.html", {})

else:

    fields = cgi.FieldStorage()
    target_domain = fields["domain"].value
    logs = []
    successful = False

    dfp_helper = sandbox.dfp_helper

    logging.info("User %r is attempting to associate with domain %r", user.nickname(), target_domain)

    try:
        discovery_url = dfp_helper.discovery_url_for_domain(target_domain)
        if discovery_url:
            logs.append("Discovery URL for this domain is %s" % discovery_url)
            try:
                associate_endpoint = dfp_helper.associate_endpoint_for_domain(target_domain)
            except dfp.DiscoveryError:
                logs.append("Discovery failed.")
            if associate_endpoint:
                logs.append("Associate endpoint for this domain is %s" % associate_endpoint)
                association = dfp_helper.request_association_for_domain(target_domain)
                if association:
                    if "token" in association:
                        if "expires_in" in association:
                            logs.append("Association endpoint responded with an association that expires in %i seconds" % int(association["expires_in"]))
                            successful = True
                        else:
                                logs.append("Association endpoint responded but didn't include expires_in")
                    else:
                        logs.append("Association endpoint responded but didn't include token")
        else:
            logs.append("Couldn't determine the discovery URL for the domain")
    except urllib2.HTTPError, ex:
        logs.append("HTTP request returned %s" % str(ex.code))
        logging.debug("Payload is %r", ex.read())
    except urllib2.URLError, ex:
        logs.append("Encountered an error during HTTP request: %s" % str(ex))
    except Exception, ex:
        logs.append("Encountered an error that wasn't handled nicely: %s" % str(ex))

    for line in logs:
        logging.info(line)

    sandbox.template_response("try_associate_result.html",
                              {"target_domain":target_domain,
                               "successful":successful,
                               "logs":logs
                               })



