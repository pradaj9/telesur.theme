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
            console.log(max_h);
            carousel.height(max_h);

            carousel.scrollable({size:4, items: '.carousel-dummy'});
        }        
    }
});
