function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


$(document).ready(function(){
    $(".button-collapse").sideNav();
    $('.modal').modal();

    
    var csrftoken = getCookie('csrftoken');
    
        //Ajax Setup
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

    // Ticket validation confirmation
    $('.seller-validate-bet').click(function(e){
        e.preventDefault();

        if( $('.ticket-number-input').val() == '' ){
            alertify.alert('Erro', 'Você deve informar o número do ticket.')
        }else{

            alert_msg = 'Confirma a validação do ticket? \n Essa ação não pode ser desfeita.'
            alertify.confirm('Confirmação', alert_msg , 
            function(){ 
                alertify.success('Confirmação realizada') 
                //TODO
            }, 
            function(){ 
                alertify.error('Cancelado')
            });
        }
    });


    $('.seller-pay-bet').click(function(e){
        e.preventDefault();

        if( $('.ticket-pay-input').val() == '' ){
            alertify.alert('Erro', 'Você deve informar o número do ticket.')
        }else{

            alert_msg = 'Confirma o pagamento do ticket? \n Essa ação não pode ser desfeita.'
            alertify.confirm('Confirmação', alert_msg , 
            function(){ 
                alertify.success('Confirmação realizada') 
                //TODO
            }, 
            function(){ 
                alertify.error('Cancelado')
            });
        }
    });

    if(Cookies.get('ticket_games') == undefined){
        Cookies.set('ticket_games', {'ticket_games':[]} );
    }
 
    $('.cotation').click(function(obj){

        var game_id = $(this).parent().siblings().first().children('.table-game-id').text().trim();
        var game_name = $(this).parent().siblings().first().children('.table-game-name').text().trim();
        var cotation_id = $(this).siblings().first().text();
        var game_start_date = $(this).parent().siblings().first().children('.table-game-start-date').text().trim();
        var game_cotation_name = $(this).siblings().eq(1).text().trim();
        var game_cotation_value = $(this).text().trim();

        var cookies = Cookies.getJSON('ticket_games');

        console.log( $.inArray(game_id, cookies['ticket_games']) );

        if(! ($.inArray(String(game_id), cookies['ticket_games']) > -1) ){

            
            cookies['ticket_games'].push(game_id);
            Cookies.set('ticket_games', cookies )
            console.log( cookies )

            //console.log( $(this).parent().siblings().first().children('.table-game-name').text().trim() )

            //new bet html
            var bet_html = '<div class="divider"></div>' +
                '<li class="center-align bet">' +
                    '<div class="game-name">' +
                        game_name +
                    '</div>' +
                    '<div class="game-start-date">' +
                        game_start_date +
                    '</div>' +
                    '<div class="game-cotation">' +
                        game_cotation_name + ' : ' + game_cotation_value +
                    '</div>' +
                    '<div class="bet-delete">' +
                        '<span class="valign-wrapper red-text">Remover' +
                            '<i class="small material-icons red-text">delete</i>' +
                        '</span>' +
                    '</div>' +
                '</li>';

            $('.ticket-list').append(bet_html);
            $('.ticket-list').append('<div class="divider"></div>');


            $.post('/add_bet/' + cotation_id, function(data, status, rq){
                //console.log(data);
                //console.log(rq.status);

                if(!rq.status == 201){
                    alertify.alert("Erro no sistema, nos avise pelo email: pabllobeg@gmail.com")
                }

            }, 'text');

        }// endif

    });


});
        
