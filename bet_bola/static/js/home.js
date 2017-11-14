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
 
});
        
