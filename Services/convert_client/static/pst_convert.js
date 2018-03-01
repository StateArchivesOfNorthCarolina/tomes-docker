/*
File: pst_convert.js
Author: Jeremy M. Gibson <jeremy.gibson@ncdcr.gov>
Description:

Controls the processes for the pst-server module of the TOMES project

 */
const GET_LIST = 1;
const SEND_PACKAGE = 2;
const PROG_ON = 3;
const PROG_OFF = 4;
const RECVED_MSG = 5;
const SOURCE_BROWSER = window.location.host;
const SERVER_LOCATION = SOURCE_BROWSER + ":9000";
var connect_s;
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
        onClick: handlePstFile
    }
};

var nodes;
var file_name;

window.onload = function() {
    connect_s = new WebSocket("ws://"+ SERVER_LOCATION);
    connect_s.onmessage = function (evt) {
        var j = JSON.parse(evt.data);
        message_router(j['router'], j['data']);
    };
    $("#account_name").val("");
};

$(document).ready(function () {
    $("#btn_submit").click(function(){
        connect_s.send(submit_opts());
        return false;
    });

    $("#main_menu").each(function () {
        $(this).find("a.item.active").removeClass("active");
    });

    $("#pst_convert").addClass("active");

    $('.ui.progress')
        .progress({
            duration : 0,
            total    : 100,
            value: 99,
            autoSuccess: false
        });

});

function message_router(type, payload) {
    switch (type) {
        case(GET_LIST):
            nodes = JSON.parse(payload);
            $.fn.zTree.init($("#treeDemo"), setting, nodes);
            break;
        case(RECVED_MSG):
            write_to_stdout(payload);
            break;
        case(PROG_ON):
            set_prog_on();
            break;
        case(PROG_OFF):
            set_prog_off();
            break;
    }
    return false;
}

function handlePstFile(event, treeId, treeNode) {
    file_name = treeNode.name;
    var name = file_name.split(".")[0];
    var date = new Date();
    var d = date.getFullYear().toString() + "_" + (date.getMonth()+ 1).toString() + "_" + date.getDate().toString();
    $("#account_name").val(name + "_" + d);
    $("#progress_from_server").append(name + " is selected for conversion <br/>");
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

function submit_opts() {
    var $opts = {
        file_name: file_name,
        acc_name: $("#account_name").val()
    };
    return to_jsn(SEND_PACKAGE, $opts);
}

function to_jsn(o, s) {
    return JSON.stringify({"o": o, "data": s});
}

function write_to_stdout(payload) {
    if (line_buffer < 50) {
        $("#progress_from_server").append(payload + '<br>')
    } else {
        $("#progress_from_server").html('');
        line_buffer = 0
    }
    line_buffer++;
    return false;
}
