"""Provides ORM Models corresponding to the object types
used by the application

"""
import json
import uuid
import time

import constants

from urlparse import urlparse
from google.appengine.ext import ndb

from exceptions import ValidationError


class ModelJSONEncoder(json.JSONEncoder):
    """Provides custom JSON encoding of NDB models

    """
    def default(self, obj):
        if hasattr(obj, 'to_serializable_dict'):
            return obj.to_serializable_dict()
        return super(ModelJSONEncoder, self).default(obj)


class BaseModel(ndb.Model):
    """Provides basic functionality such as timestamps and object_id
    generation for all models.

    """
    created = ndb.IntegerProperty()
    updated = ndb.IntegerProperty()
    object_id = ndb.StringProperty()

    def _pre_put_hook(self):
        if not self.created:
            self.created = int(time.time())
        self.updated = int(time.time())
        if not self.object_id:
            self.object_id = str(uuid.uuid4())

    @classmethod
    def get_by_object_id(cls, object_id):
        return cls.query().filter(cls.object_id==object_id).get()

    def to_serializable_dict(self):
        """Converts the model data to a serializable dict

        Define self.HIDDEN_PROPERTIES as any properties to exclude!

        """
        return self.to_dict(exclude=getattr(self, 'HIDDEN_PROPERTIES', []),)


class MonitoredURL(BaseModel):
    """Stores URLs that are currently being monitored by the service

    """
    # Indicates the monitoring interval - e.g. a value of 5 means every 5 minutes
    interval = ndb.IntegerProperty()
    # Indicates the timeout for each ping to this URL
    # Defaults to constants.STANDARD_TIMEOUT
    timeout = ndb.IntegerProperty()
    # Contains the raw URL to ping
    url = ndb.StringProperty()

    def _pre_put_hook(self):
        """Before saving ensure the URL is valid and
        not already in the database.

        """
        try:
            parsed_url = urlparse(self.url)
        except:
            # XXX: interpolate URL and make unicode safe
            raise ValidationError('Invalid URL format!')
        else:
            self.url = parsed_url.geturl()

        existing_url = MonitoredURL.query().filter(
            url=self.url,
        ).get()
        if existing_url:
            # XXX: interpolate URL and make unicode safe
            raise ValidationError('That URL is already monitored!')

        # Ensure that the interval is an allowed interval
        if self.interval not in constants.ALLOWED_MONITORING_INTERVALS:
            raise ValidationError('That monitoring interval is not allowed!')

        super(MonitoredURL, self)._pre_put_hook()


class URLDataPoint(BaseModel):
    """Stores a single data point gathered about a MonitoredURL
    at a point in time, or for a period in time if data must
    be truncated.

    """
    # Foreign Key to MonitoredURL.object_id
    url_object_id = ndb.StringProperty()
    # Identifies the minute for which this data point was captured,
    # as identified by the central monitoring process
    monitoring_timestamp = ndb.StringProperty()
    # Provides data about the status of the URL
    json_data = ndb.TextProperty()

    # XXX: Validating monitoring_timestamp and json_data
