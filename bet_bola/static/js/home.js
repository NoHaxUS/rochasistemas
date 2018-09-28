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
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }


    function removerAcentos(s){
        var map={"â":"a","Â":"A","à":"a","À":"A","á":"a","Á":"A","ã":"a","Ã":"A","ê":"e","Ê":"E","è":"e","È":"E","é":"e","É":"E","î":"i","Î":"I","ì":"i","Ì":"I","í":"i","Í":"I","õ":"o","Õ":"O","ô":"o","Ô":"O","ò":"o","Ò":"O","ó":"o","Ó":"O","ü":"u","Ü":"U","û":"u","Û":"U","ú":"u","Ú":"U","ù":"u","Ù":"U","ç":"c","Ç":"C"};
        return s.replace(/[\W\[\] ]/g,function(a){return map[a]||a});
        };

        
    $('#print_ticket').click(function(e){
    command = $(this).attr('command');
    console.log(command)
    console.log(this)
    window.location = 'intent://' + encodeURI(removerAcentos(command))
    });


    var csrftoken = getCookie('csrftoken');

    if (Cookies.get('ticket_cookie') == undefined) {
        Cookies.set('ticket_cookie', {});
    }
    RenderTicket();
    UpdateCotationTotal();

    $('.carousel.carousel-slider').carousel(
        {
            fullWidth: true,
            duration:30
        }
    );


    $("#cellphone_register").mask("(99)99999-999?9");
    $("#telefone").mask("(99)99999-999?9");
    $(".button-collapse").sideNav();
    $('.modal').modal();

        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
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

    function LightenDarkenColor(col, amt) {
  
        var usePound = false;
      
        if (col[0] == "#") {
            col = col.slice(1);
            usePound = true;
        }
     
        var num = parseInt(col,16);
     
        var r = (num >> 16) + amt;
     
        if (r > 255) r = 255;
        else if  (r < 0) r = 0;
     
        var b = ((num >> 8) & 0x00FF) + amt;
     
        if (b > 255) b = 255;
        else if  (b < 0) b = 0;
     
        var g = (num & 0x0000FF) + amt;
     
        if (g > 255) g = 255;
        else if (g < 0) g = 0;
     
        return (usePound?"#":"") + String("000000" + (g | (b << 8) | (r << 16)).toString(16)).slice(-6);
    }

    function rgb2hex(rgb) {
        rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
        return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
       }
       
    function hex(x) {
        var hexDigits = new Array
        ("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"); 
        return isNaN(x) ? "00" : hexDigits[(x - x % 16) / 16] + hexDigits[x % 16];
    }

    ORIGINAL_COTATION_COLOR = $('span.cotation').first().css('background-color');

    function selectOnClick(actualElement){

        var actual_color_hex = rgb2hex(ORIGINAL_COTATION_COLOR);
        var new_color = LightenDarkenColor(actual_color_hex, -100)
        actualElement.parent().parent().find('div > span.cotation').css('background-color', ORIGINAL_COTATION_COLOR);
        actualElement.css('background-color', new_color);
    }

    $('.cotation').click(function (e) {

        var game_id = $(this).parent().parent().siblings().first().children('.table-game-id').text().trim();
        var game_name = $(this).parent().parent().siblings().first().children('.table-game-name').text().trim();
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
        selectOnClick($(this));

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
            location.reload(true);
            

        }, function(){
            alertify.notify('Cancelado');
        }).set('movable', false);
    });

    $('.btn-bet-submit').on('click', function(e){
        e.preventDefault();

        var open_anon_modal = $("#open_anon_modal").attr('is');
    

        if($(this).attr('desktop') == 'True'){
            ticket_value = $('.ticket-bet-value-desktop').val();
        }else{
            ticket_value = $('.ticket-bet-value-mobile').val();                
        }

        if(open_anon_modal == 'true'){
            $('#modal-anon-user').modal('open');
        }else{
            var accepted_conditions = '';
            var confirmation_message = 'Confirmar aposta ?';
            CreateBetTicket(ticket_value, accepted_conditions, confirmation_message);
        }
    });

    $(".create-ticket-anon").click(function(){

        if($(".btn-bet-submit").attr('desktop') == 'True'){
            ticket_value = $('.ticket-bet-value-desktop').val();
        }else{
            ticket_value = $('.ticket-bet-value-mobile').val();                
        }

        var accepted_conditions = '';
        var confirmation_message = 'Confirmar aposta ?';
        CreateBetTicket(ticket_value, accepted_conditions, confirmation_message);

    });


    function CreateBetTicket(ticket_value, accepted_conditions, confirmation_message){

        $('#modal-anon-user').modal('close');

        var client_name = $('.client_name').val();
        var telefone = $('.telefone').val();
        var ticket = Cookies.get('ticket_cookie');


        if (ticket_value <= 0 || ticket_value == ''){
            alertify.error("Você deve apostar um valor maior que 0");
            return;
        }

        if(ticket == '{}'){
            alertify.error("Nenhuma cota selecionada nessa sessão");
            COTATION_TOTAL = 0;
            RenderTicket();
            UpdateCotationTotal();
            return;
        }
        console.log(confirmation_message);                               
        alertify.confirm('Confirmação', confirmation_message, function(){                   
        $.post('/ticket/',
        {'ticket_value': ticket_value, 
        'client_name':client_name, 
        'telefone':telefone,
        'accepted_conditions':accepted_conditions},
            function(data, status, rq){
                
                if(data.success){
                    alertify.alert("Sucesso", data.message).set('movable', false);
                }else{

                    if(data.clear_cookies){
                        Cookies.set('ticket_cookie', {});
                        window.location = '/';
                    }

                    if(data.has_to_accept){
                        var accepted_conditions = 'True';
                        var confirmation_message = data.message;
                        CreateBetTicket(ticket_value, accepted_conditions, confirmation_message);
                    }else{
                        alertify.alert("Erro", data.message);
                    }         
                                      
                }
            }, 'json');
        },function(){
            alertify.error('Cancelado');
        }).set('labels', {ok:'OK',cancel:'Cancelar'}).set('movable', false);
    }


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

    $('ul.championship-list li a').each(function(i,e){
        
        var url_array = window.location.pathname;
        var href = $(e).attr('href');
        if(url_array == href){

            $(e).css('color', $('.nav-wrapper').css('background-color'));
            $(e).css('font-weight','bold');
        }

    });


    $('#check-ticket-form').on('submit', function(e){
        
        e.preventDefault();
        var ticket_num = $('.check-ticket-input').val();
        if (ticket_num == '') {
            alertify.alert('Erro', 'Você deve informar o número do ticket.').set('movable', false);
        }else{
            var Url = '/ticket/' + ticket_num + '/';
            $(this).attr('action', Url);
            $(this).submit();
        }
    });

    $('#validate-ticket-form').on('submit', function(e){

        e.preventDefault();
        var ticket_num = $('#validate-ticket-input').val();
        if (ticket_num == '') {
            alertify.alert('Erro', 'Você deve informar o número do ticket.').set('movable', false);
        }else{

            alertify.confirm("Confirmação", "Deseja validar o Ticket: " + ticket_num, 
            function(){
                alert("OK");
            },
            function(){
                
            });
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
            } ).set('movable', false);
            

        }).fail(function(rq, status, error){
            console.log(rq.responseJSON);
            var erros = '';
            for(erro in rq.responseJSON.data){
                erros += rq.responseJSON.data[erro] + '<br>'
            }
            console.log(erros);
            alertify.alert("Erro", erros ).set('movable', false);
        });
    });


    $('#form-core-login').on('submit', function(e){
        e.preventDefault();
        var form = $(this);
        var send_data = form.serialize();

        $.post(form.attr('data-action'),
        send_data, 
        function(response, status, rq){
            if (response.success){
                
                alertify.alert('Sucesso', response.message, function(){
                    window.location = '/';
                    Cookies.set('ticket_cookie', {});
                }).set('movable', false);
            }else{
                alertify.alert('Erro', response.message ).set('movable', false);
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
