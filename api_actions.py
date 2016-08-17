"""Provides function calls that directly map to the 
API

"""
import ndb_models
import constants
import exceptions


def list_urls(
    page_size,
    page_number,
    monitoring_interval,
):
    """List all URLS with an interval matching *monitoring_interval*.

    Results are paginated, *page_size* per page, displaying the results on *page_number*

    *page_number* is 1-indexed, NOT 0-indexed

    """
    return ndb_models.MonitoredURL.query().filter(
        interval=monitoring_interval,
    ).fetch(
        limit=page_size,
        offset=(page_number-1)*page_size,
    )


def add_url(
    url,
    monitoring_interval,
    timeout,
):
    """Add a URL, *url*, to be monitored every *monitoring_interval* minutes, timing out if the request is not completed in *timeout*
    seconds

    """
    # Ensure there is capacity to add this URL
    if get_queue_workers_needed() > constants.MAX_QUEUE_WORKERS:
        raise exceptions.NoCapacityError('The system is at capacity and cannot add this URL!')

    new_url = ndb_models.MonitoredURL()
    new_url.url = url
    new_url.interval = monitoring_interval
    new_url.timeout = timeout
    new_url.put()


def get_queue_workers_needed():
    """Returns the number of queue workers needed to accomodate
    all URLs in the system at max demand

    """
    


def ping_urls(url_object_ids):
    """Synchronously and in order, ping the MonitoredURLs referenced by *url_object_ids*. Finally record a URLDataPoint for each

    """
    pass


def get_url_data_points(
    url_object_id,
    start_timestamp,
    end_timestamp,
):
    """Retrieve all URLDataPoint(s) for the MonitoredURL referenced by
    *url_object_id* between *start_timestamp* (inclusive) and *end_timestamp* (non-inclusive)

    """
    pass


def merge_data_points(
    url_object_id,
    max_data_points,
):
    """Merge together URLDataPoints for the
    MonitoredURL referenced by *url_object_id*, so that the
    total number of URLDataPoints doesn't exceed *max_data_points*.
    This is done by adding the status codes in the JSON frequency maps. The
    timestamp used for the merged URLDataPoint is the earliest.

    """
    pass
