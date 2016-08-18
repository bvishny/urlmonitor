#!/usr/bin/env python
import json
import webapp2

import exceptions
import api_actions

from webapp2_extras import (
    jinja2,
)

class BaseHandler(webapp2.RequestHandler):
    """Provides easy access to a basic templating system
    for all web handlers.

    """
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, **template_args):
        self.response.write(self.jinja2.render_template(filename, **template_args))


class APIHandler(BaseHandler):
    """Encapsulates calling of the functions in api_actions.py
    and serialization of the result

    """
    def __init__(self, path, api_function):
        self.url_path = path
        self.api_function = api_function

    def get(self):
        return self._handle(method='GET')

    def post(self):
        return self._handle(method='POST')

    def _handle(self, method):
        try:
            output = self.api_function(**getattr(self.request, method, {}))
        except Exception, e:
            if isinstance(e, exceptions.NoCapacityError):
                self.response.set_status(409)
            elif isinstance(e, exceptions.ValidationError):
                self.response.set_status(400)
            else:
                self.response.set_status(500)
            self.response.write(json.dumps({'error': unicode(e)}))
        else:
            self.response.write(json.dumps(output, cls=ndb_models.ModelJSONEncoder))


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


handlers = [
    ('/', MainHandler),
]

api_methods = [
    api_actions.list_urls,
    api_actions.add_url,
    api_actions.get_queue_workers_needed,
    api_actions.ping_urls,
    api_actions.get_url_data_points,
    api_actions.merge_data_points,
]
for method in api_methods:
    handler = APIHandler(path='/api/%s' % method.__name__, api_function=method)
    handlers.append((handler.url_path, handler))

app = webapp2.WSGIApplication(handlers, debug=True)
