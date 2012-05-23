$(document).ready(function() {

    //If we are in the homepage
    if ($('.template-home-view')[0] !== undefined) {
    
        //add layout for scrolling
        //only add scroller if we have more than 4 news
        if ( $(".articles-carousel .article-item").length > 4 ){        
            var carousel = $(".articles-carousel .articles-carousel-wrapper");
            carousel.css({'float':'left'});
            carousel.append('<div class="carousel-dummy"/>')
            var carousel_wrapper = $('.articles-carousel-wrapper .carousel-dummy');

            //add the next and prev buttons
            $('.articles-carousel').prepend('<a class="prev browse left"></a>');
            $('.articles-carousel').append('<a class="next browse left"></a>');

            var articles = $(".articles-carousel .article-item").detach();
            $(articles).each(function(i, article){
                if (i%4 === 0){
                    carousel_wrapper.append('<div class="items-wrapper" />');
                }
                var step = carousel_wrapper.find('.items-wrapper:last');            
                step.append($(this));
                
            });
            
            //set height of carousel
            var max_h = 0;
            $(".articles-carousel .article-item").each(function(){
                var h = $(this).height();
                if (h > max_h) {
                    max_h = h;
                }
            });
            carousel.height(max_h);

            carousel.scrollable({size:4, items: '.carousel-dummy'});
        }        
    }

    //video widget
    if ($('.mini-video-widget-launch')[0] != undefined) {
        var video_slug = $('.mini-video-widget-launch').attr('data-slug');
        
        var videos_dom = $('<div class="video">\
                                <a href="" class="video-link" target="_blank"><img src=""/>\
                                <span class="video-title"></span></a>\
                            </div>');
        if (video_slug) {
            //lets create the widget, its almost safe, we have an slug. 
            //The worst case scenario is not data returned from the api.. 
            $('.mini-video-widget-launch').before(
                '<div class="mini-video-widget">\
                    <h3 class="title">Videos</h3>\
                    <div class="videos">\
                        <div class="mini-videos-wrapper">\
                        </div>\
                    </div>\
                    <div class="widget-controls">\
                        <a class="left"></a>\
                        <a class="right"></a>\
                    </div>\
                </div>'
            );
        }
        var url_query = 'http://multimedia.tlsur.net/api/clip/';
        var query = {
            'detalle':'basico',
            'tema':video_slug
        }

        $.ajax({
            dataType: "jsonp",
            url: url_query,
            data: query,
            success: function(data){
                //create markup
                $(data).each(function(i, video_obj){
                    var video_markup = videos_dom.clone();
                    video_markup.find('a').attr('href', video_obj.navegador_url);
                    video_markup.find('img').attr('src', video_obj.thumbnail_mediano);
                    video_markup.find('.video-title').html(video_obj.titulo);

                    $('.mini-videos-wrapper').append(video_markup);
                });
                
                //widget setup
                var videos = $('.mini-videos-wrapper').find('.video');
                var step_width =  videos.width();
                var step = 0;
                var videos_length = videos.length;
                $('.widget-controls .left').click(function(){
                    var v = $(this).parent('.widget-controls').siblings('.videos');
                    step--;
                    if (step >= 0){
                        v.animate({scrollLeft: step_width * step});
                    } else {
                        step++;
                    }
                });
                $('.widget-controls .right').click(function(){
                    var v = $(this).parent('.widget-controls').siblings('.videos');
                    step++;
                    if ( step < videos_length ){
                        v.animate({scrollLeft: step_width * step});
                    } else {
                        step--;
                    }
                });
            }
        });
    }
    
    //video widget wide
    if ($('.wide-video-widget-launch')[0] != undefined) {
        var video_slug = $('.wide-video-widget-launch').attr('data-slug');
        
        var videos_dom = $('<div class="video">\
                                <a href="" class="video-link" target="_blank"><img src=""/>\
                                <span class="video-title"></span></a>\
                            </div>');
        if (video_slug) {
            //lets create the widget, its almost safe, we have an slug. 
            //The worst case scenario is not data returned from the api.. 
            $('.wide-video-widget-launch').before(
                '<div class="wide-video-widget">\
                    <h3 class="title">Últimos Videos</h3>\
                    <div class="videos">\
                        <div class="wide-videos-wrapper">\
                        </div>\
                    </div>\
                </div>'
            );
        }
        var url_query = 'http://multimedia.tlsur.net/api/clip/';
        var query = {
            'detalle':'basico',
            'tema':video_slug
        }

        $.ajax({
            dataType: "jsonp",
            url: url_query,
            data: query,
            success: function(data){
                //create markup
                $(data).each(function(i, video_obj){
                    if (i < 3){
                        var video_markup = videos_dom.clone();
                        video_markup.find('a').attr('href', video_obj.navegador_url);
                        video_markup.find('img').attr('src', video_obj.thumbnail_pequeno);
                        video_markup.find('.video-title').html(video_obj.titulo);

                        $('.wide-videos-wrapper').append(video_markup);
                    }
                });
            }
        });
    }
});
