//CONTROL CODES
const RECV_STD_OUT = 1;
const RECV_PROG_ON = 2;
const RECV_PROG_OFF = 3;
//END_CONTROL_CODES

//OUTGOING
const ELASTIC_ON = 100;
const ELASTIC_OFF = 101;

//INCOMING
const SELECTED_ACCOUNT = 200;
const ACCOUNT_FOUND = 201;
const ACCOUNT_NOT_FOUND = 202;


//DEFAULTS
const SOURCE_BROWSER = window.location.host;
const SERVER_LOCATION = SOURCE_BROWSER + ":9004";

var connect_s;
var account_selected;
var line_buffer = 0;

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
};

$(document).ready(function () {
    $(function(){
        $("#start_elastic").click(function(){
            connect_s.send(to_jsn(ELASTIC_ON, ''));
            return false;
        });

        $("#stop_elastic").click(function(){
            connect_s.send(to_jsn(ELASTIC_OFF, ''));
            return false;
        });
    });
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
        case(ACCOUNT_FOUND):
            $("#start_stop").css("visibility", "visible");
            break;
    }
}

function write_to_stdout(payload) {
    if (line_buffer < 50) {
        $("#message_from_server").append(payload + '<br/>')
    } else {
        $("#message_from_server").html('');
        line_buffer = 0
    }
    line_buffer++;
    return false;
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