jq17(document).ready(function() {
    //topic autocomplete
    var source_jsonp = [];
    var source_slugs= {};
    jq17('.typeahead').typeahead({
        source: function(typeahead, query){
            $.ajax({
                dataType: "jsonp",
                url:'http://multimedia.tlsur.net/api/tema/?texto='+query, 
                success: function(data){
                    var source_jsonp = [];
                    $(data).each(function(el){
                        source_jsonp.push(this.nombre);
                        source_slugs[this.nombre] = this.slug;
                    });
                    typeahead.process(source_jsonp);
                }
            });
        },
        onselect: function (obj) {
            $("input[name='topic-slug']").val(source_slugs[obj]);
            console.log(obj, source_slugs[obj]);
        }
    });
    
    //news autocomplete

});
