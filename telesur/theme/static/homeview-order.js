$(document).ready(function() {

    //only for homepage
    if ($('.template-home-view')[0] != undefined) {

        //style for primary news dragabble items
        $('.article-item').css({
            'border':'1px dashed green',
            'padding':'10px 0',
            'margin':'0 2px',
            'width':'160px'
        });
        $( ".articles-carousel-wrapper" ).sortable({
            update: function(event, ui) {
                var position = $('.article-item').index(ui.item);
                var uuid = ui.item.attr('class').split(' ').pop();
                
                $.ajax({
                    url: '@@home-set-order',
                    data: {'uuid': uuid, 'delta':position, 'key':'primary'},
                    success: function(data) {
                    }
                });
            }
        }).disableSelection();

        //style for secondary news dragabble items
        $('.notas-sencilla-grande').css({
            'border':'1px dashed green',
            'padding':'0',
            'margin': '0 2px 2px 0'
        });

        var secondary_news = $('.notas-sencilla-grande').detach();
        $('.article-listing').html(secondary_news);

        $( ".article-listing" ).sortable({
            update: function(event, ui) {
                var position = $('.notas-sencilla-grande').index(ui.item);
                var uuid = ui.item.attr('class').split(' ').pop();
                
                $.ajax({
                    url: '@@home-set-order',
                    data: {'uuid': uuid, 'delta':position, 'key':'secondary'},
                    success: function(data) {
                    }
                });
            }
        }).disableSelection();
    }
});
