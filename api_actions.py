"""Provides function calls that directly map to the 
API

"""
import math
import json
import time

import ndb_models
import constants
import exceptions

from decimal import Decimal

from google.appengine.ext import ndb
from google.appengine.api import (
    urlfetch,
    urlfetch_errors,
    taskqueue,
)


def get_urls(
    page_size,
    page_number,
    monitoring_interval,
):
    """List all URLS with an interval matching *monitoring_interval*.

    Results are paginated, *page_size* per page, displaying the results on *page_number*

    *page_number* is 1-indexed, NOT 0-indexed

    """
    base_query = ndb_models.MonitoredURL.query().filter(
        interval=monitoring_interval,
    )
    total_count = base_query.count()
    total_pages = int(math.ceil(Decimal(total_count) / Decimal(page_size)))

    if (
        page_number > total_pages and
        not (page_number == 1 and total_pages == 0)
    ) or page_number < 1:
        raise exceptions.ValidationError('Invalid page number!')

    return {
        'total_count': total_count,
        'total_pages': total_pages,
        'page_number': page_number,
        'page_size': page_size,
        'urls': base_query.fetch(
            limit=page_size,
            offset=(page_number-1)*page_size,
        ),
    }


def add_url(
    url,
    monitoring_interval=constants.STANDARD_MONITORING_INTERVAL,
    timeout=constants.STANDARD_TIMEOUT,
):
    """Add a URL, *url*, to be monitored every *monitoring_interval* minutes, timing out if the request is not completed in *timeout*
    seconds

    """
    # Ensure there is capacity to add this URL
    if get_queue_workers_needed(offset=timeout) > constants.MAX_QUEUE_WORKERS:
        raise exceptions.NoCapacityError('The system is at capacity and cannot add this URL!')

    new_url = ndb_models.MonitoredURL()
    new_url.url = url
    new_url.interval = monitoring_interval
    new_url.timeout = timeout
    new_url.put()


def get_queue_workers_needed(offset=0):
    """Returns the number of queue workers needed to accomodate
    all URLs in the system at max demand plus an additional *offset*
    seconds latency

    """
    # Oddly, Google Query Language doesn't support sum...
    return int(math.ceil(
        (
            sum([
                Decimal(url.timeout) for url in ndb_models.MonitoredURL.query().fetch()
            ]) + 
            Decimal(offset)
        ) /
        Decimal('60.0')
    ))
    

def ping_urls(url_object_ids, monitoring_timestamp):
    """Synchronously and in order, ping the MonitoredURLs referenced by *url_object_ids*. Finally record a URLDataPoint for each
    recording URLDataPoint.monitoring_timestamp = *monitoring_timestamp*

    """
    constructed_query = ndb.OR(*tuple([
        ndb_models.MonitoredURL.object_id==object_id
        for object_id in url_object_ids
    ]))
    url_objects = ndb_models.MonitoredURL.query(constructed_query)
    for url_object in url_objects:
        try:
            result = urlfetch.fetch(
                url=url_object.url,
                deadline=url_object.timeout,
            )
        except urlfetch_errors.DeadlineExceededError:
            status_code = constants.URL_TIME_OUT
        except urlfetch.Error:
            # XXX: Add more specific error codes
            status_code = constants.URL_INACCESSIBLE
        else:
            status_code = result.status_code
        finally:
            data_point = ndb_models.URLDataPoint()
            data_point.url_object_id = url_object.object_id
            data_point.monitoring_timestamp = monitoring_timestamp
            data_point.json_data = json.dumps({status_code: 1})
            data_point.put()


def run_cron_monitoring_job(is_synchronous=False):
    """Kicks off workers to ping all MonitoredURLs in the system. 

    is_synchronous is a Boolean which indicates whether to collect
    URL data WITHOUT background workers, running URL batches in
    serialized fashion instead.

    """
    # The timestamp used on the URLDataPoint(s)
    monitoring_timestamp = int(time.time())

    # Each worker should process the number of URLs that can safely be processed in a minute.
    page_size = int(math.floor(Decimal(60) / Decimal(constants.STANDARD_TIMEOUT)))
    page_number = 1
    total_pages = None
    total_urls = 0

    while not total_pages or page_number <= total_pages:
        # Right now all the URLs have a monitoring interval of 1 minute
        get_url_response = get_urls(
            page_size=page_size,
            page_number=page_number,
            monitoring_interval=constants.STANDARD_MONITORING_INTERVAL,
        )
        total_pages = get_url_response['total_pages']
        url_object_ids = [url['object_id'] for url in get_url_response['urls']]
        ping_url_params = dict(
            url_object_ids=url_object_ids,
            monitoring_timestamp=monitoring_timestamp,
        )
        if is_synchronous:
            ping_urls(**ping_url_params)
        else:
            taskqueue.add(url='/api/ping_urls', params=ping_url_params, target='worker')
        page_number += 1
        total_urls += len(url_object_ids)

    # Indicate the number of URLs queued for pinging and the number workers req'd
    return {
        'total_urls': total_urls,
        'total_workers': total_pages,
    }


def get_url_data_points(
    url_object_id,
    start_timestamp=None,
    end_timestamp=None,
):
    """Retrieve all URLDataPoint(s) for the MonitoredURL referenced by
    *url_object_id* between *start_timestamp* (inclusive) and *end_timestamp* (non-inclusive)

    """
    model = ndb_models.URLDataPoint
    conditions = [model.url_object_id==url_object_id]
    if start_timestamp:
        conditions.append(model.created>=start_timestamp)
    if end_timestamp:
        conditions.append(models.created<end_timestamp)

    constructed_query = ndb.AND(*tuple(conditions))
    return model.query(constructed_query)


def merge_data_points(
    url_object_id,
    max_data_points,
):
    """Merge together URLDataPoints for the MonitoredURL referenced by *url_object_id*,
    so that the total number of URLDataPoints doesn't exceed *max_data_points*.
    This is done by adding the status codes in the JSON frequency maps. The
    timestamp used for the merged URLDataPoint is the one from the earliest
    URLDataPoint that was combined.

    Rather than equalizing the number of URLDataPoints over time, the
    least recent URLDataPoints are meged together to hit *max_data_points*
    total URLDataPoints.

    """
    pass
