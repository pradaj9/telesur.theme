$(document).ready(function() {
    var description = $('#formfield-form-widgets-IDublinCore-description');
    if (description[0] !== undefined) {
        $('label', description).after('<span class="letter-counter">Cantidad de caracteres: <span class="caracteres">0</span></span>');
        var caracteres = $(description).find('.caracteres');
        var letter_counter = $(description).find('.letter-counter');
        caracteres.css({
            'font-size':'14px',
            'padding':'10px'
        });
        letter_counter.css({
            'float':'right',
            'font-weight':'bold'
        });
        
        var field_to_check = $('#formfield-form-widgets-IDublinCore-description').find('#form-widgets-IDublinCore-description');
        
        field_to_check.keyup(function(event){
            var number = $(this).val().length;
            caracteres.html(number);
            
            if ( number < 225) {
                caracteres.css({
                    'background-color':'white'
                });
            }
            if ( 225 <= number && number <= 250){
                caracteres.css({
                    'background-color':'green'
                });
            } else {
                if ( 300 > number && number > 250) {
                    caracteres.css({
                        'background-color':'yellow'
                    });
                } else {
                    if (number >= 300) {
                        caracteres.css({
                            'background-color':'red'
                        });                
                    }
                }
           }
        });
    }
});
