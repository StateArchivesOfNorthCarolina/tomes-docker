/*
File: nlp_convert.js
Author: Jeremy M. Gibson <jeremy.gibson@ncdcr.gov>
Description:

Controls the processes for the tomes_server module of the TOMES project

 */

//CONTROL CODES
const RECV_STD_OUT = 1;
const RECV_PROG_ON = 2;
const RECV_PROG_OFF = 3;
const RECV_FILE_LIST = 5;
//END_CONTROL_CODES

//OUTGOING/INCOMING CODES
const SEND_FILE_LOC = 4;
//DEFAULTS
const SOURCE_BROWSER = window.location.host;
const SERVER_LOCATION = SOURCE_BROWSER + ":9002";
var connect_s;
var account_selected;
var line_buffer = 0;

/*
 the setting variable is used to initialize the ztree object
 */
var setting = {
    data: {
        simpleData: {
            enable: false
        }
    },

    callback: {
        onClick: handleEaxsAccount
    }
};

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
        $("#account_list").change(function (e) {
            var theFiles = this.files;
            var relativePath = theFiles[0].webkitRelativePath;
            folder = relativePath.split("/");
        });

        $("#btn_submit").click(function(){
            var $jsn = submit_opts();
            connect_s.send($jsn);
            return false;
        });

        $("#main_menu").each(function () {
            $(this).find("a.item.active").removeClass("active");
        });

        $("#nlp_convert").addClass("active");

<<<<<<< HEAD
=======

>>>>>>> master
        $('.ui.progress')
            .progress({
                duration : 0,
                total    : 100,
                value: 99,
                autoSuccess: false
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
        case(RECV_FILE_LIST):
            nodes = JSON.parse(payload);
            $.fn.zTree.init($("#account_list"), setting, nodes);
            break;
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

function handleEaxsAccount(event, treeId, treeNode) {
    var account_file = treeNode.name;
    account_selected = account_file;
    account_file = account_file.split(".")[0];
    $("#selected_name").val(account_selected.toString());
    $("#tagged_name").val(account_file + "_tagged.xml");
    return false;
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
    $("#progress_from_server").html('');
    $("#progress_from_server").html('<h4>Complete!</h4>');
}

function to_jsn(o, s) {
    return JSON.stringify({"o": o, "data": s});
}