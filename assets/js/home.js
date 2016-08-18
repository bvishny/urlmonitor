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
