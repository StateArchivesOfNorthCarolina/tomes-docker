const SEND_PACKAGE = 1;
const STD_OUT = 2;
const PROG_ON = 3;
const PROG_OFF = 4;
const SUG_NAME = 5;
const SOURCE_BROWSER = window.location.host;
const SERVER_LOCATION = SOURCE_BROWSER + ":9001";
var connect_s;
var folder;
var account_selected;
var line_buffer = 0;

window.onload = function() {
    try {
        connect_s = new WebSocket("ws://"+ SERVER_LOCATION);
    } catch (err) {
        connect_s = new WebSocket("ws://127.0.0.1:9001");
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
        fldr: account_selected,
        chunk: $("#chunk").prop('checked'),
        stitch: $("#stitch").prop('checked'),
        no_sub: $("#no_sub").prop('checked'),
        from_eml: $("#from_eml").prop('checked'),
        trans_name: $("#trans_name").val(),
        chunk_size: $("#chunk_size").val()
    };
    return to_jsn(SEND_PACKAGE, $opts);
}

function message_router(type, payload) {
    switch (type) {
        case(SEND_PACKAGE):
            generate_table(payload);
            break;
        case(STD_OUT):
            write_to_stdout(payload);
            break;
        case(PROG_ON):
            set_prog_on();
            break;
        case(PROG_OFF):
            set_prog_off();
            break;
        case(SUG_NAME):
            set_suggested(payload);
            break;
    }
}

function write_to_stdout(payload) {
    if (line_buffer < 500) {
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

function getfolder(e) {
    var files = e.target.files;
    var path = files[0].webkitRelativePath;
    account_selected = path.split("/")[0];
    $("#account_sel").html("Account Selected: <strong>"+ account_selected +"</strong>");
    $("#account_sel").css('visibility', 'visible');
    //Return false keeps the Websocket from reseting.

    //Suggest a TransferName
    connect_s.send(to_jsn(5, {fldr: account_selected}));
    return false;
}