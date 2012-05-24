jq17(document).ready(function() {
    //managment overlays
    if ($('.administrar-portadas')[0] !== undefined){
        $('.administrar-portadas .link-overlay').prepOverlay(
            {
                subtype: 'ajax',
                filter: '.cover-control-bar'
            }
        );
    }

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
        }
    });
    
    //news autocomplete
    var source_jsonp = [];
    var source_uuid= {};
    jq17('.typeahead-news').typeahead({
        source: function(typeahead, query){
            $.ajax({
                dataType: "json",
                url:'@@news-list-search?text='+query, 
                success: function(data){
                    var source_jsonp = [];
                    $.each(data, function(uuid){
                        source_jsonp.push(this.title);
                        source_uuid[this.title] = {
                            'uuid': this.uuid,
                            'url': this.url
                        };
                    });
                    typeahead.process(source_jsonp);
                }
            });
        },
        onselect: function (obj) {
            $("input[name='outstanding-new-uid']").val(source_uuid[obj].uuid);
            $("input[name='outstanding-new']").val(source_uuid[obj].url);
        }
    });
});
