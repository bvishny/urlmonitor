$("#add_url").submit(function(e)
{
    var data = {},
        action = $(this).attr("action");

    $.each(this.elements, function(i, v){
        var input = $(v),
            attrName = input.attr("name");
        if (attrName) data[attrName] = input.val();
    });

    $.ajax({
        url : action,
        type: "POST",
        data : JSON.stringify(data),
        success:function(data, statusText, xhr) 
        {
            $('#add-url-result').html('<strong style="color:white">URL Successfully Added!</strong>');
        },
        error: function(xhr, statusText, error) 
        {
            var errorJSON = JSON.parse(xhr.responseText);
            alert('Error: ' + errorJSON.error);    
        }
    });
    e.preventDefault();
});

$('#url-list').pagination({
    dataSource: '/api/get_urls?monitoring_interval=1',
    locator: 'urls',
    callback: function(data, pagination) {
        var html = "";
        for (var idx in data) {
            var url_object = data[idx];
            html += '<a href="/histogram?object_id=' + url_object.object_id + '" class="list-group-item">' + url_object.url + '</a>';
        }
        $('#url-list-inner').html(html);
    },
    alias: {
        pageNumber: 'page_number',
        pageSize: 'page_size'
    },
    // XXX: Bad
    pageSize: 200,
})

