$(document).ready(function () {
    
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
    
        var csrftoken = getCookie('csrftoken');
    
        //Ajax Setup
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    
        $(".button-collapse").sideNav();
        $('.modal').modal();
    
        // Ticket validation confirmation
        $('.seller-validate-bet').click(function (e) {
            e.preventDefault();
    
            if ($('.ticket-number-input').val() == '') {
                alertify.alert('Erro', 'Você deve informar o número do ticket.');
            } else {
    
                alert_msg = 'Confirma a validação do ticket? \n Essa ação não pode ser desfeita.'
                alertify.confirm('Confirmação', alert_msg,
                    function () {
                        alertify.success('Confirmação realizada');
                        //TODO
                    },
                    function () {
                        alertify.error('Cancelado');
                    });
            }
        });
    
    
        $('.seller-pay-bet').click(function (e) {
            e.preventDefault();
    
            if ($('.ticket-pay-input').val() == '') {
                alertify.alert('Erro', 'Você deve informar o número do ticket.')
            } else {
    
                alert_msg = 'Confirma o pagamento do ticket? \n Essa ação não pode ser desfeita.'
                alertify.confirm('Confirmação', alert_msg,
                    function () {
                        alertify.success('Confirmação realizada');
                        //TODO
                    },
                    function () {
                        alertify.error('Cancelado');
                    });
            }
        });
    
        // define cookie if it's the first time on the page
        if (Cookies.get('ticket_cookie') == undefined) {
            Cookies.set('ticket_cookie', {});
        }
    
        function UpdateCotationTotal(){
            ticket = Cookies.getJSON('ticket_cookie');
            var total = 1;
        
            for (var key in ticket){
                var cotation_value = parseFloat( (ticket[key]['cotation_value']).replace(',','.') );
                total = total * cotation_value;
                //console.log( ticket[key]['cotation_value'].replace(',','.') );
            }
            if(total == 1) total = 0;
            $('.cotation-total').text( parseFloat( total.toFixed(2) ) );
    
            COTATION_TOTAL = parseFloat( total.toFixed(2) ) ;
            $('#ticket-bet-value').trigger('keyup');
            
        }
    
        function AddBetToTicket(bet_info) {
            var ticket = Cookies.getJSON('ticket_cookie'); // {}
            ticket[bet_info['game_id']] = bet_info;
            Cookies.set('ticket_cookie', ticket);
    
            UpdateCotationTotal();
            RenderTicket();
            $('#ticket-bet-value').trigger('keyup');
        }
    
        function RenderTicket() {
    
            ticket = Cookies.getJSON('ticket_cookie');
    
            $('.ticket-list').empty();
    
            for (var key in ticket) {
    
                //new bet html
                var bet_html = '<div class="divider"></div>' +
                    '<li class="center-align bet">' +
                    '<div class="game-id hide">'+
                        ticket[key]['game_id'] +
                    '</div>'+
                    '<div class="game-name">' +
                        ticket[key]['game_name'] +
                    '</div>' +
                    '<div class="game-start-date">' +
                        ticket[key]['game_start_date'] +
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
    
    
        RenderTicket();
        UpdateCotationTotal();
    
        $('#ticket-bet-value').keyup(function(data){
    
            var ticket_bet_value = parseFloat($(this).val());
        
            if( isNaN(ticket_bet_value) ){
                $('.award-value').text('R$ 0.00');
            }else{
                var award_value = (COTATION_TOTAL * ticket_bet_value).toFixed(2);
                $('.award-value').text('R$ ' + award_value);
            }
        });
    
        $(document).on("click",'.bet-delete', function(){
            ticket = Cookies.getJSON('ticket_cookie');
    
            game_id_to_delete = $(this).siblings().first().text().trim();
    
            delete ticket[game_id_to_delete];
            Cookies.set('ticket_cookie', ticket);
            RenderTicket();
            UpdateCotationTotal();
            $('#ticket-bet-value').trigger('keyup');
            //console.debug(Cookies.getJSON('ticket_cookie'));

            $.ajax({
                url: '/bet/' + game_id_to_delete,
                method: 'DELETE',
                complete: function(jqXR) {
                    console.log(jqXR.status);
                }
            });

        });

        $('.more-cotation').click(function(e){



        });
    
        $('.cotation').click(function (e) {
    
            var game_id = $(this).parent().siblings().first().children('.table-game-id').text().trim();
            var game_name = $(this).parent().siblings().first().children('.table-game-name').text().trim();
            var game_start_date = $(this).parent().siblings().first().children('.table-game-start-date').text().trim();
            var cotation_id = $(this).siblings().first().text();
            var cotation_name = $(this).siblings().eq(1).text().trim();
            var cotation_value = $(this).text().trim();
    
            bet_info = {
                'game_id': game_id,
                'game_name': game_name,
                'game_start_date': game_start_date,
                'cotation_id': cotation_id,
                'cotation_name': cotation_name,
                'cotation_value': cotation_value
            }
    
            AddBetToTicket(bet_info);
    
            //console.debug(Cookies.getJSON('ticket_cookie'));
    
                $.post('/bet/', bet_info, function(data, status, rq){
                    console.log(data);
                    console.log(rq.status);
    
                }, 'text');
    
        });

        $('.btn-bet-submit').on('click', function(){
            var ticket = Cookies.get('ticket_cookie');

            var ticket_value = $('#ticket-bet-value').val();

            if(ticket == '{}'){
                alertify.error("Nenhuma cota selecionada nessa sessão.");
                COTATION_TOTAL = 0;
                RenderTicket();
                UpdateCotationTotal();
            }else{

                $.post('/bet_ticket/', {'ticket_value': ticket_value} , function(data, status, rq){
                    
                    var dataJSON = jQuery.parseJSON(data);

                    if(dataJSON.status == 401){
                        $('#modal-login').modal('open');
                    }
                    if(dataJSON.status == 403){
                        console.log('test');
                        alertify.error("Selecione cotas antes de apostar.");
                    }
                    if(dataJSON.status == 400){
                        alertify.alert("Erro", "Erro ao tentar processar essa requisição. \n Por favor avise-nos pelo email: pabllobeg@gmail.com");
                    }
                    if(dataJSON.status == 201){
                        alert('OK');
                    }
                    console.log(dataJSON.status);
                }, 'text');
            }

        });

        $('.more_cotations_button').on('click', function(e){

            $('#more-cotations').modal('open');

            var game_id = $(this).siblings().first().children('.table-game-id').text().trim();
            var game_name = $(this).siblings().first().children('.table-game-name').text().trim();
            var game_start_date = $(this).siblings().first().children('.table-game-start-date').text().trim();
        
            $('.more_cotation_header').text(game_name);

            var game_data = '<tr>' +
                '<td class="hide more-game-id">'+ game_id +'</td>' +
                '<td class="hide more-game-name">'+ game_name +'</td>'+
                '<td class="hide more-game-start-date">'+ game_start_date +'</td>'+
            '</tr>';

            //console.log(game_data);
            $('.more-table tbody').empty().append(game_data);

            $.get('/cotations/'+ game_id, function(data, status, rq){
                
                var dataJSON = jQuery.parseJSON(data);

                var full_html = '';
                for( key in dataJSON){
                    
                    var more_cotation_html = '<tr>' +
                    '<td class="hide">'+ dataJSON[key].pk + '</td>' +
                    '<td>'+ dataJSON[key].fields.name + '</td>' +
                    '<td class="more-cotation">'+ dataJSON[key].fields.value +'</td>' +
                     '</tr>';
                     full_html += more_cotation_html;
                };

                $('.more-table tbody').append(full_html);


                //console.log(dataJSON);
                //console.log(rq.status);
                
            }, 'text');
                
        });

        $(document).on('click', '.more-cotation',function(){
            var first_tr = $(this).parent().parent().children().first();
            var game_id = first_tr.children('.more-game-id').text().trim();
            var game_name = first_tr.children('.more-game-name').text().trim();
            var game_start_date = first_tr.children('.more-game-start-date').text().trim();
            var cotation_id = $(this).siblings().eq(0).text();
            var cotation_name = $(this).siblings().eq(1).text();
            var cotation_value = $(this).text().trim();

            console.debug(cotation_id);

            bet_info = {
                'game_id': game_id,
                'game_name': game_name,
                'game_start_date': game_start_date,
                'cotation_id': cotation_id,
                'cotation_name': cotation_name,
                'cotation_value': cotation_value
            }

            AddBetToTicket(bet_info);

            $('#more-cotations').modal('close');

        });


    });
    
    