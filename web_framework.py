import json
import webapp2
import copy

import errors
import api_actions
import ndb_models

from webapp2_extras import (
    jinja2,
)

from helpers import string_bool_converter


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
    # Specifies typed parameters
    PARAMS_TO_CONVERT = {
        'page_size': int,
        'page_number': int,
        'monitoring_interval': int,
        'timeout': int,
        'offset': int,
        'monitoring_timestamp': int,
        'is_synchronous': string_bool_converter,
        'start_timestamp': int,
        'end_timestamp': int,
        'max_data_points': int,
    }

    @property
    def api_method(self):
        # XXX: TERRIBLE
        for api_method in api_actions.ALLOWED_API_METHODS:
            if api_method.__name__ in str(self.request.path):
                return api_method

    @property
    def is_get_allowed(self):
        return (
            self.api_method.__name__.startswith('get_') or
            self.api_method.__name__.startswith('run_cron_')
        )

    def get(self):
        return self._handle(method='GET')

    def post(self):
        return self._handle(method='POST')

    def _handle(self, method):
        try:
            # Ensure that the proper HTTP method is used
            if int(self.is_get_allowed) + int(method=='GET') == 1:
                raise errors.ValidationError('Invalid HTTP method!')
            # Convert parameters as needed
            if method == 'POST':
                request_data = json.loads(self.request.body.decode('utf-8'))
            else:
                request_data = dict(self.request.GET)

            for k, v in request_data.iteritems():
                if k in self.PARAMS_TO_CONVERT:
                    request_data[k] = self.PARAMS_TO_CONVERT[k](v)

            # XXX: Hack, Remove '_' param
            request_data.pop('_', None)

            output = self.api_method(**request_data)
        except Exception, e:
            if isinstance(e, errors.NoCapacityError):
                self.response.set_status(409)
                error_message = unicode(e)
            elif isinstance(e, errors.ValidationError):
                self.response.set_status(400)
                error_message = unicode(e)
            else:
                # XXX: REMOVE
                raise e
                self.response.set_status(500)
                # Do not expose raw error message - potentially confidential
                error_message = unicode('Unable to process request - please contact us')
            self.response.write(json.dumps({
                'error_class': e.__class__.__name__,
                'error': error_message,
            }))
        else:
            self.response.write(json.dumps(output, cls=ndb_models.ModelJSONEncoder))
