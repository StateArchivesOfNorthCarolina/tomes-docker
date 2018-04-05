//CONTROL CODES
const RECV_STD_OUT = 1;
const RECV_PROG_ON = 2;
const RECV_PROG_OFF = 3;
//END_CONTROL_CODES

//OUTGOING
const SND_ELASTIC_ON = 100;
const SND_ELASTIC_OFF = 101;
const SND_IS_ELASTIC_ON = 103;
const SND_LOAD_ACCOUNT = 104;
const SND_INDEX_ACCOUNT = 105;

//INCOMING
const SELECTED_ACCOUNT = 200;
const ACCOUNT_FOUND = 201;
const ACCOUNT_NOT_FOUND = 202;
const RECV_ELASTIC_OFF = 203;
const RECV_ELASTIC_ON = 204;
const RECV_ACCOUNTS_FOUND = 205;
const RECV_ACCOUNTS_NOT_FOUND = 206;


//DEFAULTS
const SOURCE_BROWSER = window.location.host;
const SERVER_LOCATION = SOURCE_BROWSER + ":9004";

var connect_s;
var account_selected;
var line_buffer = 0;
var server_state = 0;
var initial_check = 0;

window.onload = function() {
    try {
        connect_s = new WebSocket("ws://"+ SERVER_LOCATION);
    } catch (err) {
        connect_s = new WebSocket("ws://127.0.0.1:9004");
    }


    connect_s.onmessage = function (evt) {
        var j = JSON.parse(evt.data);
        message_router(j['router'], j['data']);
    };

    connect_s.onopen = function () {
        connect_s.send(to_jsn(SND_IS_ELASTIC_ON, ''));
    };

    if (server_state === false) {
        change_checkbox();
    }

};

$(document).ready(function () {
    $(function(){
        let chxbx = $('.ui.checkbox');
        chxbx.checkbox({
                onChecked: function () {
                    server_state = true;
                    change_checkbox();
                },
                onUnchecked: function () {
                    server_state = false;
                    change_checkbox();
                }
            })
        });

    $("#elastic_activate").click(function () {
        turn_elastic_on();
    })

});


function message_router(type, payload) {
    switch (type) {
        case(RECV_STD_OUT):
            write_to_stdout(payload);
            break;
        case(RECV_PROG_ON):
            set_prog_on();
            break;
        case(RECV_PROG_OFF):
            set_prog_off();
            break;
        case(RECV_ELASTIC_OFF):
            server_state = false;
            $('.ui.checkbox').checkbox('uncheck');
            $("#ss_slider").text("ElasticSearch Off");
            $("#ss_slider").css("color", "red");
            break;
        case(RECV_ELASTIC_ON):
            server_state = true;
            $('.ui.checkbox').checkbox('check');
            $("#ss_slider").text("ElasticSearch On");
            $("#ss_slider").css("color", "green");
            break;
        case(ACCOUNT_FOUND):
            $("#start_stop").css("visibility", "visible");
            break;
        case(RECV_ACCOUNTS_FOUND):
            accounts_tables(JSON.parse(payload), 1);
            break;
        case(RECV_ACCOUNTS_NOT_FOUND):
            accounts_tables(JSON.parse(payload), 2);
            break;
    }
}


function accounts_tables(accounts, table) {
    for(var i = 0; i < accounts.length; i++) {
        var location = accounts[i];
        var name = location.split('\\').pop().split('/').pop();
        switch (table) {
            case(1):
                $("#elastic_accounts").find('tbody').append(get_table_row(location, name, table));
                break;
            case(2):
                $("#elastic_no_accounts").find('tbody').append(get_table_row(location, name, table));
                break;
        }
    }
}

function get_table_row(location, name, type) {
    var row = $("<tr>");
    row.append($("<td>").html(name));
    row.append($("<td>").html(location));
    if(type === 1) {
        var button = $("<td>").attr('class', 'single line');
        button.append(build_button(location, type));
    } else {
        var button = $("<td>").attr('class', 'single line');
        button.append(build_button(location, type));
    }
    row.append(button);
    return row;
}

function build_button(acct, type) {
    if(type === 1) {
        var mybutton = $("<button>").attr('class', 'ui primary button').html("Load Account").click(function () {
            handle_button(acct, type);
        });
    } else {
        var mybutton = $("<button>").attr('class', 'ui primary button').html("Create Indexes").click(function () {
            handle_button(acct, type);
        });
    }
    return mybutton;
}

function handle_button(acct, type) {
    switch (type){
        case(1):
            connect_s.send(to_jsn(SND_LOAD_ACCOUNT, acct));
            break;
        case(2):
            connect_s.send(to_jsn(SND_INDEX_ACCOUNT, acct));
            break;
    }
}

function write_to_stdout(payload) {
    if (line_buffer < 50) {
        $("#progress_from_server").append(payload + '<br/>')
    } else {
        $("#progress_from_server").html('');
        line_buffer = 0
    }
    line_buffer++;
    return false;
}

function change_checkbox() {
    if (server_state === true) {
        $("#ss_slider").text("ElasticSearch On");
        $("#ss_slider").css("color", "green");
    } else {
        $("#ss_slider").text("ElasticSearch Off");
        $("#ss_slider").css("color", "red");
    }
}

function turn_elastic_on() {
    connect_s.send(to_jsn(SND_ELASTIC_ON, ''))
}

function set_prog_on() {
    $("#prog_bar").css("visibility", "visible");
}

function set_prog_off() {
    $("#prog_bar").css("visibility", "hidden");
}

function to_jsn(o, s) {
    return JSON.stringify({"o": o, "data": s});
}

function getfolder(e) {
    var files = e.target.files[0].webkitRelativePath;
    account_selected = files.split("/")[0];
    $("#account_sel").html("Account Selected: <strong>"+ account_selected +"</strong>");
    $("#account_sel").css('visibility', 'visible');
    connect_s.send(to_jsn(SELECTED_ACCOUNT, account_selected));
    return false;
}