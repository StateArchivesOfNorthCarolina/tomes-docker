//CONTROL CODES
const RECV_STD_OUT = 1;
const RECV_PROG_ON = 2;
const RECV_PROG_OFF = 3;
//END_CONTROL_CODES

//OUTGOING/INCOMING CODES
const SEND_FILE_LOC = 4;
//DEFAULTS
const SOURCE_BROWSER = window.location.host;
const SERVER_LOCATION = SOURCE_BROWSER + ":9002";
var connect_s;
var account_selected;
var line_buffer = 0;

window.onload = function() {
    try {
        connect_s = new WebSocket("ws://"+ SERVER_LOCATION);
    } catch (err) {
        connect_s = new WebSocket("ws://127.0.0.1:9002");
    }

    connect_s.onmessage = function (evt) {
        var j = JSON.parse(evt.data);
        message_router(j['router'], j['data']);
    };
};

$(document).ready(function () {
    $(function(){
        $("#mbox_dir").change(function (e) {
            var theFiles = this.files;
            var relativePath = theFiles[0].webkitRelativePath;
            folder = relativePath.split("/");
        });

        $("#btn_submit").click(function(){
            var $jsn = submit_opts();
            connect_s.send($jsn);
            return false;
        });

    });
});

function submit_opts() {
    var $opts = {
        eaxs_file: account_selected,
        out_file: $("#tagged_name").val()
    };
    return to_jsn(SEND_FILE_LOC, $opts);
}

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

function set_prog_on() {
    $("#prog_bar").css("visibility", "visible");
}

function set_prog_off() {
    $("#prog_bar").css("visibility", "hidden");
}

function set_suggested(sug) {
    $("#trans_name").val(sug.toLowerCase());
}

function to_jsn(o, s) {
    return JSON.stringify({"o": o, "data": s});
}

function getfile(e) {
    var files = e.target.files;
    account_selected = files[0].name;
    $("#account_sel").html("EAXS Selected: <strong>"+ account_selected +"</strong>");
    $("#account_sel").css('visibility', 'visible');
    //Return false keeps the Websocket from reseting.

    //Suggest a TransferName
    //connect_s.send(to_jsn(5, {eaxs_file: account_selected}));
    return false;
}