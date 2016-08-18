function renderGraph(objectId, containerId) {
    // First load the data
    $.ajax({
        url : '/api/get_url_data_points?url_object_id=' + objectId,
        type: "GET",
        success:function(data, statusText, xhr) 
        {
            var dataPoints = JSON.parse(xhr.responseText),
                dataByStatus = {};

            // Make a first pass and determine all status codes present
            for (var idx in dataPoints) {
                var dataPoint = dataPoints[idx],
                    frequencies = JSON.parse(dataPoint.json_data);

                for (var k in frequencies) {
                    if (dataByStatus[k] === undefined) {
                        dataByStatus[k] = [];
                    }
                }
            }
            // Make a second pass and fill in data
            for (var idx in dataPoints) {
                var dataPoint = dataPoints[idx],
                    frequencies = JSON.parse(dataPoint.json_data);

                for (var k in dataByStatus) {
                    dataByStatus[k].push({
                        'x': parseInt(dataPoint.monitoring_timestamp),
                        'y': (frequencies[k] !== undefined) ? parseInt(frequencies[k]) : 0
                    });
                }
            }
            var series = [];
            for (var k in dataByStatus) {
                series.push({
                    color: '#0099FF',
                    data: dataByStatus[k],
                    name: k.toString()
                });
            }
            var graph = new Rickshaw.Graph( {
                element: document.getElementById(containerId),
                width: 960,
                height: 500,
                renderer: 'line',
                series: series
            });

            graph.render();

            var hoverDetail = new Rickshaw.Graph.HoverDetail({
                graph: graph
            });

            var legend = new Rickshaw.Graph.Legend({
                graph: graph,
                element: document.getElementById('legend'),
            });

            var shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
                graph: graph,
                legend: legend,
            });

            var axes = new Rickshaw.Graph.Axis.Time({
                graph: graph,
            });
            axes.render();
        },
        error: function(xhr, statusText, error) 
        {
            var errorJSON = JSON.parse(xhr.responseText);
            alert('Error: ' + errorJSON.error);    
        }
    });
}