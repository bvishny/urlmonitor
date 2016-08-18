#!/usr/bin/env python
import json
import webapp2

import errors
import api_actions
import ndb_models

from web_framework import (
    BaseHandler,
    APIHandler,
)

class MainHandler(BaseHandler):
    """The Homepage of the service, allows the addition
    of new MonitoredURL(s) and listing of existing MonitoredURL(s)

    """
    def get(self):
        return self.render_template('home.html')


class HistogramHandler(BaseHandler):
    """Displays a graph of the frequency of different HTTP status
    codes over time

    """
    def get(self):
        url = ndb_models.MonitoredURL.get_by_object_id(self.request.get('object_id'))
        return self.render_template(
            'url_histogram.html',
            url=url
        )


handlers = [
    ('/', MainHandler),
    ('/histogram', HistogramHandler),
]

for method in api_actions.ALLOWED_API_METHODS:
    url_path = '/api/%s' % method.__name__
    handlers.append((url_path, APIHandler))

app = webapp2.WSGIApplication(handlers, debug=True)
