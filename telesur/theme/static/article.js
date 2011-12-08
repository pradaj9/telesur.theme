jq(function($) {

    /*comments fix*/
    //if ($('.comment-counter .counter').html() === "0") {
    //    $('.comment-counter .counter').addClass('empty');
    //}

    /*first we have to check if we have videos*/
    
    if ($('#video-galery-container .scrollable-video-galery img')[0] !== undefined) {
        /*we have to pre preocess the html in order to get the correct gallery disposition*/
        
        /*lest do a relatinship thumb => video*/
        $('#video-galery-container .scrollable-video-galery .thumb-image').each(function(){
            $(this).data('video', $(this).parent('.video-widget'));
        });
        
        /*moving thumbs into his own div*/
        var thumbs = $('#video-galery-container .scrollable-video-galery .thumb-image').detach();
        var items = $('.scrollable-video-galery').append('<div class="items"/>').find('.items');
        items.html(thumbs);
        
        /*moving videos outside the container into the video wrapper*/
        var videos = $('.scrollable-video-galery .video-widget').detach();
        $('.videos-wrapper').html(videos);
        
        /*lets hide all the videos but the first*/
        $('.videos-wrapper .video-widget').css('display', 'none').filter(":first").css('display', 'block');
        
        $(".video-counter .counter").prepOverlay({
            subtype:'inline',
            target: '#video-galery-container'
        });

        $("#video-galery-container").scrollable({size: 4});
        
        
        /*functionality for the gallery*/
        /*thumbs selectors*/
        $('.items .thumb-image').click(function(){
            $('.videos-wrapper .video-widget').hide();
            $(this).data('video').show();
        });
    }
            
});
