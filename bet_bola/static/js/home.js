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
 

    $('.cotation').click(function(obj){

        var id = $(this).siblings().first().text();
        var csrftoken = getCookie('csrftoken');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $.post('/add_bet/' + id, function(data, status, rq){
            if(!rq.status == 201){
                alertify.alert("Erro no sistema, nos avise pelo email: pabllobeg@gmail.com")
            }
        }, 'text');

        console.log( $(this).siblings().first().text() );
    });


});
        
