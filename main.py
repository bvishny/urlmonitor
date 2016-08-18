#!/usr/bin/env python
import json
import webapp2

import errors
import api_actions
import ndb_models

from webapp2_extras import (
    jinja2,
)

from web_framework import (
    BaseHandler,
    APIHandler,
)

ALLOWED_API_METHODS = [
    api_actions.get_urls,
    api_actions.add_url,
    api_actions.get_queue_workers_needed,
    api_actions.ping_urls,
    api_actions.run_cron_monitoring_job,
    api_actions.get_url_data_points,
    api_actions.merge_data_points,
]

class MainHandler(BaseHandler):
    def get(self):
        return self.render_template(
            'home.html',
            **{}
        )


handlers = [
    ('/', MainHandler),
]

for method in ALLOWED_API_METHODS:
    url_path = '/api/%s' % method.__name__
    handlers.append((url_path, APIHandler))

app = webapp2.WSGIApplication(handlers, debug=True)
