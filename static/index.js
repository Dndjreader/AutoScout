$( document ).ready(function() {

    let sort_players = function() {

        $.ajax({
            url: "/playerdatabase",
            type: 'get',
            data: {
                sort_by: $('#sort').val(),
                asc: $('#asc').val(),
                league: $('#league').val(),
                player: $('#player-name').val()
            },
            
            success: function(response) {
                $('#players tbody').empty();
                $.each(response.players, function(index, player) {
                    $('#players tbody').append(
                        `
                        <tr>
                            <td class="text-start"><img class="thumbnail-sml" src="${player['player_face_url']}"></td>
                            <td class="text-start">${player['short_name'] }<p><img title="${player['nationality_name']}" class="flag-sml" src="${player['nation_flag_url']}"></p></td>
                            <td class="text-start">${player['age']}</td>
                            <td class="text-start">${player['player_positions']}</td>
                            <td class="text-middle rating">${player['overall']}</td>
                            <td class="text-middle rating">${player['potential']}</td>
                            <td class="text-middle"><img title="${player['club_name']}" class="club-sml" src="${player['club_logo_url'] }"> ${player['club_name'] }</td>
                            <td class="text-middle">${player['league_name']}</td>
                            <td class="text-middle">${ player['wage'] }</td>
                            <td class="text-middle">${ player['value'] }</td>
                            <td class="text-middle"><a href="/playerinfo/${ player['sofifa_id'] }">More Info >>></a></td>
                        </tr>
                        `
                    );
                });
            }
        });
    };

    $('#sort-form').on('change', sort_players);
    $('#player-name').on('change', sort_players);

    $('#username').on('change', function() {
        $.ajax({
            url: "/usercheck",
            type: 'get',
            data: {
                username: $('#username').val(),
            },

            success: function(response) {
                $('#user-error').empty();
                if (response == "true") {
                    $('#user-error').append(
                        `
                            <span class="error">Username already taken</span>
                        `
                    );
                }
                else {
                    $('#user-error').empty()
                }
            }
        });
    });

    $('#confirmation').on('change', function() {
        $('#pass-error').empty();
        let password = $('#password').val();
        let confirmation = $('#confirmation').val();
            if (password != confirmation) {
                $('#pass-error').append(
                    `
                        <span class="error">Passwords do not match</span>
                    `
                );
            }
            else {
                $('#pass-error').empty()
            }
        });

    $('#tabs button:not(:first)').addClass('inactive');
    $('.tabcontent').hide();
    $('.tabcontent:first').show();
    $('#tabs button').click(function(){
        let tab = $(this).attr('id');
        console.log('#'+ tab+ 'tab');
        if($(this).hasClass('inactive')){ //this is the start of our condition 
            $('#tabs button').addClass('inactive');           
            $(this).removeClass('inactive');
        
            $('.tabcontent').hide();
            $('#'+ tab+ 'tab').fadeIn('slow');
        }
        }); 

    let myTeamSort = function() {

        $.ajax({
            url: "/myteamdata",
            type: 'get',
            data: {
                sort_by: $('#sort-myteam').val(),
                asc: $('#asc-myteam').val(),
                player: $('#myteam-name').val(),
                team: $('#teamName').val()
            },
            
            success: function(response) {
                $('#players tbody').empty();
                $.each(response.players, function(index, player) {
                    $('#players tbody').append(
                        `
                        <tr>
                            <td class="text-start"><img class="thumbnail-sml" src="${player['player_face_url']}"></td>
                            <td class="text-start">${player['short_name'] }<p><img title="${player['nationality_name']}" class="flag-sml" src="${player['nation_flag_url']}"></p></td>
                            <td class="text-start">${player['age']}</td>
                            <td class="text-start">${player['player_positions']}</td>
                            <td class="text-middle rating">${player['overall']}</td>
                            <td class="text-middle rating">${player['potential']}</td>
                            <td class="text-middle">${ player['wage'] }</td>
                            <td class="text-middle">${ player['value'] }</td>
                            <td class="text-middle"><a href="/playerinfo/${ player['sofifa_id'] }">More Info >>></a></td>
                        </tr>
                        `
                    );
                });
            }
        });
    };

    $('#sort-myteam').on('change', myTeamSort);
    $('#asc-myteam').on('change', myTeamSort);
    $('#myteam-name').on('change', myTeamSort);

    
    $('#watchlist-btn').on('click', function() {
        $.ajax({
                url: "/addwatchlist",
                type: 'get',
                data: {
                    player: $('#watchlist-btn').val(),
                },
                success: function(response) {
                    $('#added').empty();
                    if (response == "Added") {
                        $('#added').append(
                            `
                                <span class="valid">Added!</span>
                            `
                        );
                    }
                    else if (response == "Already In Watchlist") {
                        $('#added').append(
                            `
                                <span class="error">Already in Watch List!</span>
                            `
                        );
                    }
                }
        });

    });

    $('#remove-btn').on('click', function() {
        $.ajax({
            url: "/removewatchlist",
            type: 'get',
            data: {
                player: $('#remove-btn').val(),
            },
            success: function(response) {
                $('#players tbody').empty();
                    $.each(response.players, function(index, player) {
                        $('#players tbody').append(
                            `
                            <tr>
                                <td class="text-start"><img class="thumbnail-sml" src="${player['player_face_url']}"></td>
                                <td class="text-start">${player['short_name'] }<p><img title="${player['nationality_name']}" class="flag-sml" src="${player['nation_flag_url']}"></p></td>
                                <td class="text-start">${player['age']}</td>
                                <td class="text-start">${player['player_positions']}</td>
                                <td class="text-middle rating">${player['overall']}</td>
                                <td class="text-middle rating">${player['potential']}</td>
                                <td class="text-middle"><img title="${player['club_name']}" class="club-sml" src="${player['club_logo_url'] }"> ${player['club_name'] }</td>
                                <td class="text-middle">${player['league_name']}</td>
                                <td class="text-middle">${ player['wage'] }</td>
                                <td class="text-middle">${ player['value'] }</td>
                                <td class="text-middle"><a href="/playerinfo/${ player['sofifa_id'] }">More Info >>></a></td>
                                <td class="text-middle"><button id="remove-btn" value="{{ player['sofifa_id'] }}">Remove</button></td>
                            </tr>
                            `
                        );
                    });
                }
        });
    });

    let watchSort = function() {

        $.ajax({
            url: "/watchlistData",
            type: 'get',
            data: {
                sort_by: $('#watch-sort').val(),
                asc: $('#watch-asc').val(),
                league: $('#watch-league').val(),
                player: $('#watch-name').val()
            },
            
            success: function(response) {
                $('#players tbody').empty();
                $.each(response.players, function(index, player) {
                    $('#players tbody').append(
                        `
                        <tr>
                            <td class="text-start"><img class="thumbnail-sml" src="${player['player_face_url']}"></td>
                            <td class="text-start">${player['short_name'] }<p><img title="${player['nationality_name']}" class="flag-sml" src="${player['nation_flag_url']}"></p></td>
                            <td class="text-start">${player['age']}</td>
                            <td class="text-start">${player['player_positions']}</td>
                            <td class="text-middle rating">${player['overall']}</td>
                            <td class="text-middle rating">${player['potential']}</td>
                            <td class="text-middle"><img title="${player['club_name']}" class="club-sml" src="${player['club_logo_url'] }"> ${player['club_name'] }</td>
                            <td class="text-middle">${player['league_name']}</td>
                            <td class="text-middle">${ player['wage'] }</td>
                            <td class="text-middle">${ player['value'] }</td>
                            <td class="text-middle"><a href="/playerinfo/${ player['sofifa_id'] }">More Info >>></a></td>
                            <td class="text-middle"><button id="remove-btn" value="{{ player['sofifa_id'] }}">Remove</button></td>
                        </tr>
                        `
                    );
                });
            }
        });
    };


    $('#watch-sort').on('change', watchSort);
    $('#watch-asc').on('change', watchSort);
    $('#watch-name').on('change', watchSort);
    $('#watch-league').on('change', watchSort);
});