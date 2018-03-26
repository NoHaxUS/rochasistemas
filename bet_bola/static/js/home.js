$(document).ready(function () {

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
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

        var csrftoken = getCookie('csrftoken');

        if (Cookies.get('ticket_cookie') == undefined) {
            Cookies.set('ticket_cookie', {});
        }
        RenderTicket();
        UpdateCotationTotal();


        $("#cellphone_register").mask("(99)99999-999?9");
        
        $(".button-collapse").sideNav();
        $('.modal').modal();

         $.ajaxSetup({
              beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                  }
            }
        });

        $('#validate-ticket-form').on('submit', function (e) {
            e.preventDefault();
            var send_data = $(this).serialize();
            
            if ($('.ticket-number-input').val() == '') {
                alertify.alert('Erro', 'Você deve informar o número do ticket.');
            } else {
    
                alert_msg = 'Confirma a validação do ticket? \n Essa ação não pode ser desfeita.'
                alertify.confirm('Confirmação', alert_msg,
                    function () {
                        $.post('/user/seller/validate_ticket/', send_data, function(data, status, rq){
                            data = jQuery.parseJSON(data);

                            if(data['status'] == 200){
                                alertify.success('Ticket Validado');
                            }
                            
                            if(data['status'] == 406){
                                alertify.success('Ticket já Validado.');
                            }
                            if(data['status'] == 405){
                                alertify.alert('Desculpe. Vendedor não possui limite de credito para efetuar a aposta.');
                            }
                            if(data['status'] == 404){
                                alertify.error('Ticket não encontrado');
                            }
                            if(data['status'] == 403){
                                alertify.alert('Erro', 'Esse ticket não pode mais ser validado, pois um de seus jogos já começou ou terminou.');
                            }
                            if(data['status'] == 400){
                                alertify.error('Algo deu errado.');
                            }
                        }, 'text');
                        $('#validate-bet').modal('close')
                    },
                    function () {
                        alertify.error('Cancelado');
                    });
            }
        });


    $("#reset-revenue-form").on('submit', function(e){
        e.preventDefault();

        var seller_id = $('.reset-revenue').val();


        if(seller_id == ''){
            alertify.error('ID do vendedor obrigatória');
        }else{

            $.ajax({
                url: '/reset_revenue/',
                data: {'seller_id': seller_id},
                success: function(r, textStatus, jqXR){
                    console.log(r);
                    if(r.status == 200){
                       
                    var confirm_text = 'Nome: ' + r.nome + '<br>' +
                    'CPF:' + r.cpf + '<br>' +
                    'Telefone: '+ r.telefone + '<br>' +
                    'Faturamento Atual: R$ ' + r.faturamento + '<br>';

                    alertify.confirm("Confirme os dados", confirm_text, function(){
                        
                        var seller_id = $('.reset-revenue').val();
                        $.ajax({
                            url:'/reset_revenue/',
                            method: 'POST',
                            data: {'seller_id': seller_id},
                            success: function(r, textStatus, jqXR){
                                if(r.status){
                                    alertify.alert("Sucesso", "Faturamento Zerado com sucesso!.");
                                };
                            }

                        });
                    }, function(){
                        alertify.error('Cancelado.');
                    });

                    }

                    if(r.status == 404){
                        alertify.error("Vendedor não encontrado");
                    }

                    if(r.status == 400){
                        alertify.error("Algo deu errado: " + r.status);
                    }
                }
              });
        }

    });

    $("#reduce-cotations-form").on('submit', function(e){
        e.preventDefault();
        var percent = $('.percent-reduction').val();
        if(  percent < 1 || percent > 100  ){
            alertify.alert('Erro', 'Escolha um número entre 1 e 100');
        }else{
            var load;
            $.ajax({
                url: '/utils/cotation_reduction/' + (percent / 100),
                method: 'GET',
                beforeSend: function(jqXR, settings){
                    
                    load = alertify.alert().setHeader('<em> Carregando.... </em> ')
                    .set('closable', false)
                    .set('frameless', true)
                    .setContent(
                    '<div class="preloader-wrapper big active">' +
                    '<div class="spinner-layer spinner-blue-only">' +
                        '<div class="circle-clipper left">'+
                        '<div class="circle"></div>' +
                        '</div><div class="gap-patch">' +
                        '<div class="circle"></div>' +
                        '</div><div class="circle-clipper right">' +
                        '<div class="circle"></div>' +
                        '</div>' +
                    '</div>' +
                    '</div>'+
                    '<div class="right">' +
                    'Processando... Não saia da página...' +
                    '</div>'
                
                ).show();
                },
                complete: function(jqXR, textStatus){
                    alertify.notify("Cotas alteradas com sucesso");
                    load.close();
                }
            });

        }

    });

        $('#pay-punter-form').on('submit', function (e) {
            e.preventDefault();
            var send_data = $(this).serialize();

            if ($('.ticket-pay-input').val() == '') {
                alertify.alert('Erro', 'Você deve informar o número do ticket.')
            } else {
    
                alert_msg = 'Confirma o pagamento do ticket? \n Essa ação não pode ser desfeita.'
                alertify.confirm('Confirmação', alert_msg,
                    function () {
                        
                        $.post('/user/seller/punter_payment/', send_data, function(data, status, rq){
                            
                            data = jQuery.parseJSON(data);

                            if(data.status == 200){
                                alertify.success("O Apostador foi pago com sucesso");
                            }

                            if(data.status == 401){
                                alertify.error("Você não pode recompensar um Ticket que não venceu.");
                            }

                            if(data.status == 404){
                                alertify.error('Ticket não encontrado.');
                            }
                            if(data.status == 400){
                                alertify.error('Algo deu errado.');
                            }
                        }, 'text');
        
                    },
                    function () {
                        alertify.error('Cancelado');
                    });
            }
        });

    $('.modal-credit').click(function (e) {
        seller_id = $(this).attr('data-id');
        $('#seller_id').val(seller_id);
        $('#modal-manager-credit').modal('open');
    });
    

    $('#modal-add-credit').on('submit', function (e) {                        
            e.preventDefault();
            var send_data = $(this).serialize();            
            if ($('#valor_credito').val() == '' || parseInt($('#valor_credito').val()) <= 0) {
                alertify.alert('Erro', 'Você deve inserir um valor valido positivo.')
            } else {
                alert_msg = "Deseja confirmar essa transfarencia?"
                alertify.confirm('Confirmação', alert_msg,
                    function () {
                        
                        $.post('/user/manager/credit_transfer', send_data, function(data, status, rq){
                            
                            data = jQuery.parseJSON(data);

                            alertify.confirm(data.message, function(){ location.reload() });
                        }, 'text');
        
                    },
                    function () {
                        alertify.error('Cancelado');
                    });
            }            
        });

    $('.modal-permission').click(function (e) {
        gerente_id = $(this).attr('data-id');
        $('#gerente_id').val(gerente_id);
        $('#modal-manager-permissions').modal('open');
    });

    $('#modal-add-permissions').on('submit', function (e) {                        
            e.preventDefault();
            var send_data = $(this).serialize(); 
            if( isNaN($('#vendedor_id').val()) ){
                alertify.alert('Erro', 'O ID deve ser um numero inteiro.')
            }
            else if ($('#vendedor_id').val() == '' || parseInt($('#vendedor_id').val()) <= 0) {
                alertify.alert('Erro', 'Você deve inserir um id valido.')
            } else {
                alert_msg = "Deseja adicionar essa permissão?"
                alertify.confirm('Confirmação', alert_msg,
                    function () {
                        
                        $.post('/user/config/manager_permissions', send_data, function(data, status, rq){
                            
                            data = jQuery.parseJSON(data);

                            alertify.confirm(data.message, function(){ location.reload() });
                        }, 'text');
        
                    },
                    function () {
                        alertify.error('Cancelado');
                    });
            }            
        });


        $('#modal-remove-permissions').on('submit', function (e) {                
            e.preventDefault();
            var send_data = $(this).serialize(); 
            if( isNaN($('#vendedor_id').val()) ){
                alertify.alert('Erro', 'O ID deve ser um numero inteiro.')
            }
            else if ($('#vendedor_id').val() == '' || parseInt($('#vendedor_id').val()) <= 0) {
                alertify.alert('Erro', 'Você deve inserir um id valido.')
            } else {
                alert_msg = "Deseja remover vendedor?"
                alertify.confirm('Confirmação', alert_msg,
                    function () {
                        
                        $.ajax({
                            url: '/user/config/manager_permissions',
                            type: 'DELETE',
                            data: send_data
                        }).done(function(response){
                            alertify.confirm(response.message, function(){ location.reload() });
                        });
        
                    },
                    function () {
                        alertify.error('Cancelado');
                    });
            }            
        });

        function UpdateCotationTotal(){
            ticket = Cookies.getJSON('ticket_cookie');
            var total = 1;
        
            for (var key in ticket){
                var cotation_value = parseFloat( (ticket[key]['cotation_value']).replace(',','.') );
                total = total * cotation_value;
            }
            if(total == 1) total = 0;

            $('.cotation-total').text( parseFloat( total.toFixed(2) ) );
    
            COTATION_TOTAL = parseFloat( total.toFixed(2) );

        }

        function AddBetToTicket(bet_info) {

            var ticket = Cookies.getJSON('ticket_cookie'); // {}
            ticket[bet_info['game_id']] = bet_info;
            Cookies.set('ticket_cookie', ticket);

            $.post('/bet/', bet_info, function(data, status, rq){
                console.log(rq.status);
                if(rq.status == '201'){
                    alertify.notify("Adicionado");
                }
            }, 'text');
            
            UpdateCotationTotal();
            var ticket_bet_value = parseFloat( $($('.ticket-bet-value')[0]).val() );
            updateRewardTotal(ticket_bet_value);
            RenderTicket();

        }

        function RenderTicket() {
    
            ticket = Cookies.getJSON('ticket_cookie');
    
            $('.ticket-list').empty();
    
            for (var key in ticket) {
    
                var bet_html = '<div class="divider"></div>' +
                    '<li class="center-align bet">' +
                    '<div class="game-id hide">'+
                        ticket[key]['game_id'] +
                    '</div>'+
                    '<div class="game-name">' +
                        ticket[key]['game_name'] +
                    '</div>' +
                    '<div>' +
                        ticket[key]['cotation_kind'] +
                    '</div>' +
                    '<div class="game-cotation">' +
                        ticket[key]['cotation_name'] + ' : ' + ticket[key]['cotation_value'] +
                    '</div>' +
                    '<div class="bet-delete">' +
                    '<span class="valign-wrapper red-text">Remover' +
                    '<i class="small material-icons red-text">delete</i>' +
                    '</span>' +
                    '</div>' +
                    '</li>';
    
                $('.ticket-list').append(bet_html);
                $('.ticket-list').append('<div class="divider"></div>');
            }
    
        }
    
        function updateRewardTotal(ticket_bet_value){
    
            if( isNaN(ticket_bet_value) ){
                $('.award-value').text('R$ 0.00');
            }else{
                var award_value = (COTATION_TOTAL * ticket_bet_value).toFixed(2);
                $('.award-value').text('R$ ' + award_value);
            }
        };
       

        $('.ticket-bet-value-mobile').keyup(function(data){
    
            var ticket_bet_value = parseFloat($(this).val());
            $('.ticket-bet-value-desktop').val(ticket_bet_value);
            updateRewardTotal(ticket_bet_value);

        });

        $('.ticket-bet-value-desktop').keyup(function(data){
    
            var ticket_bet_value = parseFloat($(this).val());
            $('.ticket-bet-value-mobile').val(ticket_bet_value);
            updateRewardTotal(ticket_bet_value);

        });

        $(document).on("click",'.bet-delete', function(){
            ticket = Cookies.getJSON('ticket_cookie');
    
            game_id_to_delete = $(this).siblings().first().text().trim();

            delete ticket[game_id_to_delete];
            Cookies.set('ticket_cookie', ticket);
            RenderTicket();
            UpdateCotationTotal();
            $('.ticket-bet-value').trigger('keyup');

            $.ajax({
                url: '/bet/' + game_id_to_delete,
                method: 'DELETE',
                complete: function(jqXR) {
                    console.log(jqXR.status);
                }
            });

        });

        $('.cotation').click(function (e) {
    
            var game_id = $(this).parent().siblings().first().children('.table-game-id').text().trim();
            var game_name = $(this).parent().siblings().first().children('.table-game-name').text().trim();
            var cotation_id = $(this).siblings().first().text();
            var cotation_name = $(this).siblings().eq(1).text().trim();
            var cotation_value = $(this).text().trim();
            var cotation_kind = $(this).siblings().eq(2).text().trim();
            console.log(cotation_kind);
    
            bet_info = {
                'game_id': game_id,
                'game_name': game_name,
                'cotation_id': cotation_id,
                'cotation_name': cotation_name,
                'cotation_value': cotation_value,
                'cotation_kind' : cotation_kind
            }
    
            AddBetToTicket(bet_info);
    
        });

        $('.btn-bet-undo').on('click', function(){                                

            alertify.confirm('Limpar apostas', 'Deseja mesmo limpar as apostas ?', function(){
                bet_info = {
                    'game_id': -1,
                    'game_name': '-1',
                    'cotation_id': -1,
                    'cotation_name': '-1',
                    'cotation_value': '1',
                    'cotation_kind' : '-1'
                }            
    
                AddBetToTicket(bet_info);            
                Cookies.set('ticket_cookie', {});
                RenderTicket();
                UpdateCotationTotal();
                $('.ticket-bet-value').trigger('keyup');
                alertify.notify('Feito');

            }, function(){
                alertify.notify('Cancelado');
            });
 
        });

    $('.btn-bet-submit').on('click', function(){
        var ticket = Cookies.get('ticket_cookie');


        if($(this).attr('desktop') == 'True'){
            ticket_value = $('.ticket-bet-value-desktop').val();
        }else{
            ticket_value = $('.ticket-bet-value-mobile').val();
        }

        if (ticket_value <= 0){
            alertify.error("Você deve apostar um valor maior que 0");
            return ;
        }

        console.log(ticket_value);

        if(ticket == '{}'){
            alertify.error("Nenhuma cota selecionada nessa sessão");
            COTATION_TOTAL = 0;
            RenderTicket();
            UpdateCotationTotal();
        }else{
            if(ticket_value != ''){

                alertify.confirm('Confirmação','Confirmar aposta?', function(){

                    $.post('/ticket/',
                    {'ticket_value': ticket_value},
                    (data, status, rq)=>{
                        if(data.success){
                            alertify.alert("Sucesso", data.message);
                        }else{
                            if(data.action == 'log_in'){
                                $('#modal-login').modal('open');
                            }else{
                                alertify.alert("Erro", data.message);
                            }
                        }
                    }, 'json');
                }, function(){
                    alertify.error('Cancelado');
                });
            }else{
                alertify.error("Informe o valor da sua aposta");
            }
        }
    });


    $('.btn-bet-submit-seller').on('click', function(){            
        $('#modal-random-user').modal('open');
    });

    $('.user-random').on('click', function(){      

        $('#modal-random-user').modal('close');

        var nome = $('.nome').val();
        var telefone = $('.telefone').val();
        var ticket = Cookies.get('ticket_cookie');  

        if($(this).attr('desktop') == 'True'){
            ticket_value = $('.ticket-bet-value-desktop').val();
        }else{
            ticket_value = $('.ticket-bet-value-mobile').val();                
        }   

        if (ticket_value <= 0){
            alertify.error("Você deve apostar um valor maior que 0");
            return ;
        }

        console.log(ticket_value);

        if(ticket == '{}'){
            alertify.error("Nenhuma cota selecionada nessa sessão");
            COTATION_TOTAL = 0;
            RenderTicket();
            UpdateCotationTotal();
        }else{
            if(ticket_value != ''){                                                               
                    alertify.confirm('Confirmação','Confirmar aposta?', function(){                        
                    $.post('/ticket/',
                    {'ticket_value': ticket_value, 'nome':nome, 'telefone':telefone},
                    (data, status, rq)=>{
                        
                        if(data.success){
                            alertify.alert("Sucesso", data.message);
                        }else{
                            if(data.action == 'log_in'){
                                $('#modal-login').modal('open');
                            }else{
                                alertify.alert("Erro", data.message);
                            }
                        }
                    }, 'json');
                },function(){
                    alertify.error('Cancelado');
                });
                
            }else{
                alertify.error("Informe o valor da sua aposta");
            }
        }

    });

        $('.more_cotations_button').on('click', function(e){

            $('.more_cotation_progress').show();

            $('#more-cotations').modal('open');

            var game_id = $(this).parent().siblings().first().children('.table-game-id').text().trim();
            var game_name = $(this).parent().siblings().first().children('.table-game-name').text().trim();

            $('.more_cotation_header').text(game_name);

            var game_data = '<tr>' +
                '<td class="hide more-game-id">'+ game_id +'</td>' +
                '<td class="hide more-game-name">'+ game_name +'</td>' +
            '</tr>';

            $('.more-table tbody').empty().append(game_data);

            $.get('/cotations/'+ game_id, function(data, status, rq){
                
                var dataJSON = jQuery.parseJSON(data);

                var full_html = '';

                for( key in dataJSON){

                    full_html += '<tr>' +
                    '<td class="cotation-market-label">'+ key + '</td>' +
                    '<td class="cotation-market-label"></td>' +
                    '</tr>';

                    var array_cotations = jQuery.parseJSON( dataJSON[key] )
                    var array_cotations_length = array_cotations.length;

                    for (var i = 0; i < array_cotations_length; i++) {
                        
                        full_html += '<tr>' +
                        '<td class="hide">'+ array_cotations[i].pk + '</td>' +
                        '<td class="more-cotation-name">'+ array_cotations[i].fields.name + '</td>' +
                        '<td class="more-cotation">'+ array_cotations[i].fields.value +'</td>' +
                        '<td class="more-cotation-kind hide">' + array_cotations[i].fields.kind + '</td>' +
                         '</tr>';

                    }
                    
                }

                $('.more-table tbody').append(full_html);
                $('.more_cotation_progress').hide();

            }, 'text');
                
        });

        $(document).on('click', '.more-cotation',function(){
            var first_tr = $(this).parent().parent().children().first();
            var game_id = first_tr.children('.more-game-id').text().trim();
            var game_name = first_tr.children('.more-game-name').text().trim();
            var cotation_id = $(this).siblings().eq(0).text();
            var cotation_name = $(this).siblings().eq(1).text();
            var cotation_value = $(this).text().trim();
            var cotation_kind = $(this).siblings().eq(2).text();
            console.log(cotation_kind);

   
            bet_info = {
                'game_id': game_id,
                'game_name': game_name,
                'cotation_id': cotation_id,
                'cotation_name': cotation_name,
                'cotation_value': cotation_value,
                'cotation_kind' : cotation_kind
            }

            AddBetToTicket(bet_info);

            $('#more-cotations').modal('close');

        });


        $('#check-ticket-form').on('submit', function(){
            
            var ticket_num = $('.check-ticket-input').val();
            if (ticket_num == '') {
                alertify.alert('Erro', 'Você deve informar o número do ticket.');
            }else{
                var Url = '/ticket/' + ticket_num;
                $(this).attr('action', Url);
                $(this).submit();
            }
        });

        $('ul.championship-list li a').each(function(i,e){
            
            var url_array = window.location.pathname;
            var href = $(e).attr('href');
            if(url_array == href){

                $(e).css('color','#2f9048');
                $(e).css('font-weight','bold');
            }

        });

    
        $('#user_register_form').on('submit', function(e){
            e.preventDefault();
            var send_data = $(this).serialize();

            $.post('/user/punter/register/', send_data, function(data, status, rq){
                console.log(rq.status);

                alertify.alert("Sucesso","Cadastrado com sucesso, você será logado automaticamente. Boas apostas :)")
                .set('onok', 
                function(closeEvent){
                    window.location = '/';
                } );
                

            }).fail(function(rq, status, error){
                console.log(rq.responseJSON);
                var erros = '';
                for(erro in rq.responseJSON.data){
                    erros += rq.responseJSON.data[erro] + '<br>'
                }
                console.log(erros);
                alertify.alert("Erro", erros )
            });
        });

        $('#change-pass-user-form').on('submit', function(e){
            e.preventDefault();
            var send_data = $(this).serialize();

            $.post('/user/change_password/', send_data, function(data, status, rq){
                
                if (data.status == 200){
                    alertify.alert("Sucesso", "Senha alterada com sucesso.");
                    $('#modal-change-password').modal('close');

                }
                if (data.status == 406){
                    alertify.alert("Erro", "A senha atual não confere.");
                }
            });
        });


        $('#form-core-login').on('submit', function(e){
            e.preventDefault();
            var form = $(this);
            var send_data = form.serialize();

            $.post(form.attr('data-action'),
            send_data, 
            (response, status, rq)=>{
                if (response.success){
                    
                    alertify.alert('Sucesso', response.message, ()=>{
                        window.location = '/';
                    });
                }else{
                    alertify.alert('Erro', response.message );
                }
            },
            'json'
            );
        });


        $( window ).scroll(function(){
            var top = (document.documentElement && document.documentElement.scrollTop) || 
            document.body.scrollTop;
        
            if (top > 500){
                $('#back-to-top').show();
            }
            else{
                $('#back-to-top').hide();   
            }
            
        });
        
        $('#back-to-top').each(function(){
            $(this).click(function(){ 
                $('html,body').animate({ scrollTop: 0 }, 'slow');
            });
        });

});

