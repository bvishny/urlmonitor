# urlmonitor
URL Monitor is a service that allows monitoring of a URL over time (every minute currently),
and the graphing of the status codes encountered. 

Interface
=================
You can view a list of URLs monitored and add new ones at http://sstorage-url-monitor.appspot.com/

API
==================
The following API actions are possible. Please see api_actions.py for parameters and explanations
in the docstrings:

GET get_urls
POST add_url
GET get_queue_workers_needed
POST ping_urls
GET run_cron_monitoring_job
GET get_url_data_points
POST merge_data_points

Technologies Used
==================
Backend: Python on Google App Engine
Database: Google Cloud Database (Has schema but new fields can be added by simply updating code)
Graphing Library: Rickshaw on D3

Weaknesses
===========

Flexibility:
- Currently we require all URLs to have the same monitoring interval
and a timeout under 5 seconds. If we allowed timeouts greater than 5 seconds we would
need to allocate URLs to workers in a more clever manner as there would
be the potential for a worker to NOT hit all its URLs in a minute.

Scalability:
- Due to the nature of Google App Engine's task queue, a max capacity must be set. Once the system
estimates this capacity will be hit, no additional URLs can be added. This capacity must be
arbitrarily set, and is not limitless as would be expected with auto scaling
- When the number of data points becomes too large, the browser will no longer be able to download
and graph it all. Data points need to be combined together to reduce the amount of data stored.
A method for how to do this is described in merge_data_points, however that method is not yet
implemented.

Testing:
- Although the API-first setup makes this application easily testable, automated
testing was not added due to sudden time constraints.

UI:
- The histogram color scheme changes each time the graph is generated vs. having a predictable color
for each status code. Additionally there is a low probability that two statuses
will have the same color.
