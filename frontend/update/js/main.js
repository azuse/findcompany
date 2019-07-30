

$('.button-collapse').sideNav({
    menuWidth: 300, // Default is 240
    edge: 'left', // Choose the horizontal origin
    closeOnClick: false, // Closes side-nav on <a> clicks, useful for Angular/Meteor
    draggable: true // Choose whether you can drag to open on touch screens
}
);

$('.dropdown-button-custom').dropdown({
    inDuration: 300,
    outDuration: 225,
    constrain_width: false, // Does not change width of dropdown to that of the activator
    hover: true, // Activate on hover
    gutter: 0, // Spacing from edge
    belowOrigin: false, // Displays dropdown below the button
    alignment: 'left' // Displays dropdown with edge aligned to the left of button
}
);


function show() {
    $("#showbtn").css("display", "none")
    $("#baidu").css("display", "block")
    $("#huazhan").css("display", "block")
}

var start_time
var pid_update_handler
var log_update_handler
var exec_type = "main"



function exec() {
    $.ajax({
        url: "../php/execUpdate.php",
        aysnc: true,
        data: {
            type: exec_type
        },
        success: function (res) {
        },
        fail: function () {
            Materialize.toast("执行失败", 800)

        }
    })


    Materialize.toast("开始执行", 800)
    $("#btn-exec").addClass("disabled")


    pid_update_handler =  setInterval(updateRunningImform, 5000)
    log_update_handler =  setInterval(getLog, 5000)
}

function getLog() {
    $.ajax({
        url: "../php/getLog.php",
        success: function (res) {
            // console.log(res)
            $("#log").val(res)
            var $textarea = $('#log');
            $textarea.scrollTop($textarea[0].scrollHeight);
        },
        fail: function () {
            Materialize.toast("执行失败", 800)

        }
    })
}

function updateRunningImform() {
    $.ajax({
        url: "../php/getPid.php",
        success: function (res) {


            // console.log(res)
            jsonData = JSON.parse(res)
            $("#last-execute-date")[0].innerHTML = jsonData.pid[1]


            if (jsonData.running) {
                start_time = Date.parse(jsonData.pid[1])
                now_time = jsonData.now * 1000
                var diff = now_time - start_time;

                var days = Math.floor(diff / (1000 * 60 * 60 * 24));
                diff -= days * (1000 * 60 * 60 * 24);

                var hours = Math.floor(diff / (1000 * 60 * 60));
                diff -= hours * (1000 * 60 * 60);

                var mins = Math.floor(diff / (1000 * 60));
                diff -= mins * (1000 * 60);

                var seconds = Math.floor(diff / (1000));
                diff -= seconds * (1000);

                $("#runpid")[0].innerHTML = jsonData.pid[0]
                str = ""
                if (days)
                    str += days + " 天, "
                if (hours)
                    str += hours + " 小时, "
                if (mins)
                    str += mins + " 分钟, "
                if (seconds)
                    str += seconds + " 秒"
                $("#runtime")[0].innerHTML = str
                $("#btn-kill").css("display", "block")
                $("#btn-exec").addClass("disabled")
            }
            else {
                Materialize.toast("执行失败", 800)

                $("#btn-kill").css("display", "none")
                $("#btn-exec").removeClass("disabled")

                clearInterval(pid_update_handler)
                clearInterval(log_update_handler)
            }
        },
        fail: function () {

        }
    })
}

function isRunning() {
    $.ajax({
        url: "../php/getPid.php",
        success: function (res) {
            // console.log(res)
            jsonData = JSON.parse(res)
            $("#last-execute-date")[0].innerHTML = jsonData.pid[1]
            if (jsonData.running) {
                $("#btn-kill").css("display", "block")
                $("#btn-exec").addClass("disabled")

                pid_update_handler =  setInterval(updateRunningImform, 1000)
                log_update_handler =  setInterval(getLog, 3000)
            }
            else {
                $("#btn-kill").css("display", "none")
                $("#btn-exec").removeClass("disabled")
            }
        },
        fail: function () {

        }
    })
}

function kill() {
    clearInterval(pid_update_handler)
    clearInterval(log_update_handler)
    $.ajax({
        url: "../php/killUpdate.php",
        success: function (res) {
            jsonData = JSON.parse(res)
            if(jsonData.killed){
                Materialize.toast("已终止", 800)

                $("#btn-kill").css("display", "none")
                $("#btn-exec").removeClass("disabled")

            }
        },
        fail: function () {

        }
    })
}

function restoreSession(name) {
    jsonData = localStorage.getItem(name);
    try {
        data = JSON.parse(jsonData)
    }
    catch (err) {
        console.log(err)
        data = null
    }
    return data
}

function saveSession(name, data) {
    jsonData = JSON.stringify(data)
    localStorage.setItem(name, jsonData);
}

var settings
var config
var keywordstring = ""

function restoreSettings(){
    settings = restoreSession("settings")
    if(settings == null || settings.length == 0)
    {
        settings = {}
        settings.execType = 'main'
        settings.displayOutput = false
        saveSession('settings', settings)
    }
    
    $("#displayOutput").val(settings["displayOutput"])
    if( settings['displayOutput'] == true){
        $("#outputCard").css('display','block')
        $("#displayOutput").prop('checked', true)
    }
    else{
        $("#outputCard").css('display','none')
        $("#displayOutput").prop('checked', false)
    }

    exec_type = settings['execType']
    $("input.with-gap").removeAttr("checked")
    $("#"+settings['execType']).attr( 'checked', "checked" )

    $.ajax({
        url:"../php/modifyConfig.php",
        method:"POST",
        data:{
            func:"read"
        },
        success:function(res){
            config = JSON.parse(res)
            keywords = config.BAIDU.keywords
            string = ""
            for(i in keywords){
                string += keywords[i]
                if(i != keywords.length - 1)
                    string += ","
            }
            $("#keywords").val(string)
            keywordstring = string
            time_sleep = config.BAIDU.time_sleep
            $("#time_sleep").val(time_sleep)
        }
    })
}

function saveSettings(){
    if(settings == null || typeof(settings) !== Array)
        settings = {}
    settings['displayOutput'] = $("#displayOutput").is(':checked')
    settings['execType'] = exec_type

    if( settings['displayOutput'] == true)
        $("#outputCard").css('display','block')
    else
        $("#outputCard").css('display','none')

    keywords = $("#keywords").val().split(",")
    keywords = JSON.stringify(keywords)
    time_sleep = $("#time_sleep").val()

    $.ajax({
        url:"../php/modifyConfig.php",
        method:"POST",
        data:{
            func:"write",
            keywords:keywords,
            time_sleep:time_sleep
        },
        success:function(res){ Materialize.toast("设置已保存", 500)}
    })
    
    saveSession('settings', settings)
    Materialize.toast("设置已保存", 800)

    if(keywordstring != $("#keywords").val())
        $("#do-you-want-to-wipe-database").modal('open')
}

function wipedatabase(){
    Materialize.toast("开始清空数据库", 800)
    $.ajax({
        url:"../php/wipedatabase.php",
        method:'get',
        success: function(res) {
            if(res == "success")
                Materialize.toast("已清空数据库", 800)
        }
    })
}


function updateHistory(){
    $.ajax({
        url:"../php/updateHistory.php",
        method:"get",
        success: function(res) {
            json = res;
            for(row in json){
                addId = json[row]["addId"]
                date = json[row]['date']
                type = json[row]["type"]
                resultCount = json[row]['result_count']

                if(type == 1)
                    typeName = "主更新脚本"
                else if(type == 2)
                    typeName = "华展云单独更新脚本"
                else if(type == 3)
                    typeName = "更新公司简介脚本"
                else if(type == 4)
                    typeName = "更新公司招聘信息脚本"
                else if(type == 5)
                    typeName = "脉脉脚本"

                html = "<tr><td>"+typeName+"</td><td>更新"+resultCount+"家公司</td><td>"+date+"</td><td><a href='./updateDetail.html?addId="+addId+"'>查看</a></td></tr>"
                $("#updateHistoryTbody")[0].innerHTML += html
                
            }

            $("#last-execute-date")[0].innerHTML = json[0]["date"]
            $("#last-execute-result")[0].innerHTML = "更新"+json[0]["result_count"]+"家公司"
            $("#updateDetail")[0].href = "./updateDetail.html?addId="+json[0]['addId']
        }
    })
}

restoreSettings()
updateHistory()
isRunning()
$('.modal').modal();