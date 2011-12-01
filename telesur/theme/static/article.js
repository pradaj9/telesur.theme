jq(function($) {
    $(".video-galery-container").scrollable({size: 1, circular: true,});
    
    /*ESTE JS SE LLAMA 2 VECES, CUIDADO!!!!!, probablmenete por diazo*/
    $(".video-counter a").prepOverlay({
        subtype:'inline',
        target: '#video-galery-container',
    });
            
});
