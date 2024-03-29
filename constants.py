# Indicates the standard monitoring interval in minutes
STANDARD_MONITORING_INTERVAL = 1
# Indicates the set of allowed monitoring intervals
ALLOWED_MONITORING_INTERVALS = (
    STANDARD_MONITORING_INTERVAL,
)
# Indicates the number of seconds after which to timeout a ping to a MonitoredURL
STANDARD_TIMEOUT = 5
# Indicates the maximum number of queue workers allowed
MAX_QUEUE_WORKERS = 1000
# Used in a URLDataPoint when the URL cannot be reached
URL_INACCESSIBLE = 1
# Used in a URLDataPoint when the request times out
URL_TIME_OUT = 2
