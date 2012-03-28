jq(function($) {
    /**
    * Images scrollable gallery 
    **/
	$("#images").scrollable({ circular: true, mousewheel: true });
	
	if ($('#mediabox')[0] !== undefined) {
	    $(".image-counter .counter").prepOverlay({
                subtype:'inline',
                target: '#mediabox'
        });
    }
    

    /**
    * Videos scrollable gallery 
    **/
    /*first we have to check if we have videos*/
    
    if ($('#video-galery-container .scrollable-video-galery img')[0] !== undefined) {
        /*we have to pre preocess the html in order to get the correct gallery disposition*/
        
        /*lest do a relatinship thumb => video*/
        $('#video-galery-container .scrollable-video-galery .thumb-image').each(function(){
            $(this).data('video', $(this).parent('.video-widget'));
        });
        
        /*moving thumbs into his own div*/
        var thumbs = $('#video-galery-container .scrollable-video-galery .thumb-image').detach();
        var items = $('#video-galery-container .scrollable-video-galery').append('<div class="items"/>').find('.items');
        items.html(thumbs);
        
        /*moving videos outside the container into the video wrapper*/
        var videos = $('#video-galery-container .scrollable-video-galery .video-widget').detach();
        $('#video-galery-container .videos-wrapper').html(videos);
        
        /*lets hide all the videos but the first*/
        $('#video-galery-container .videos-wrapper .video-widget').css('display', 'none').filter(":first").css('display', 'block');
        
        $(".video-counter .counter").prepOverlay({
            subtype:'inline',
            target: '#video-galery-container'
        });

        $("#video-galery-container").scrollable({size: 4});
        
        
        /*functionality for the gallery*/
        /*thumbs selectors*/
        $('#video-galery-container .items .thumb-image').click(function(){
            $('.videos-wrapper .video-widget').hide();
            $(this).data('video').show();
        });
    }
    
    
    
    
    /**
    * Audio scrollable gallery 
    **/
    /*first we have to check if we have videos*/
    
    if ($('#audio-galery-container .scrollable-video-galery img')[0] !== undefined) {
                /*we have to pre preocess the html in order to get the correct gallery disposition*/
                
                /*lest do a relatinship thumb => video*/
                $('#audio-galery-container .scrollable-video-galery .thumb-image').each(function(){
                    $(this).data('audio', $(this).parent('.audio-widget'));
                });
                
                /*moving thumbs into his own div*/
                var thumbs = $('#audio-galery-container .scrollable-video-galery .thumb-image').detach();
                var items = $('#audio-galery-container .scrollable-video-galery').append('<div class="items"/>').find('.items');
                items.html(thumbs);
                
                /*moving videos outside the container into the video wrapper*/
                var audios = $('#audio-galery-container .scrollable-video-galery .audio-widget').detach();
                $('#audio-galery-container .videos-wrapper').html(audios);
                
                /*lets hide all the videos but the first*/
                $('#audio-galery-container .videos-wrapper .audio-widget').css('display', 'none').filter(":first").css('display', 'block');
                
                $(".audio-counter .counter").prepOverlay({
                    subtype:'inline',
                    target: '#audio-galery-container'
                });
        
                $("#audio-galery-container").scrollable({size: 4});
                
                
                /*functionality for the gallery*/
                /*thumbs selectors*/
                $('#audio-galery-container .scrollable-video-galery .items .thumb-image').click(function(){
                    $('.videos-wrapper .audio-widget').hide();
                    $(this).data('audio').show();
                });
            }
            
    
    
    
    //article view, add videos from d&d widget

    if ($('.contenttreeWindow')[0] !== undefined){
        //first we have to add a new action in the add new menu
        var link = $('<li><a href="./@@media_uploader" class="contenttype-multiplefiles" id="multiplefiles" title=""><img width="16" height="16" alt="" src="++resource++telesur.theme/img/movie_play.png" title="multiplefiles"><span class="subMenuTitle">Upload videos</span></a></li>');
        jq('#plone-contentmenu-factories .actionMenuContent ul').append(link);
        
        link.click(function(event){
            event.preventDefault();
            $('.contenttreeWindow').showDialog();
        });
    }
            
});
