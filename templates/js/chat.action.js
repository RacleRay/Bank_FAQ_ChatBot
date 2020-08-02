(window.onresize = function () {
    screenFuc();
})();


// 回车键发送
$(".div-textarea").keydown(
    function (event) {
        if (event.keyCode == 13) {
            sendMessage();
            return false;
        }
    }
);


// 点击发送
$("#chat-fasong").click(function () {
    sendMessage();
});


$(".chatBox-activate").append("<div class=\"time-div\"><small>" + getTime() + "</small> </div> ")


function screenFuc() {
    var topHeight = $(".chatBox-head").innerHeight();//聊天头部高度
    //屏幕小于768px时候,布局change
    var winWidth = $(window).innerWidth();
    var chatWidth = $(".chatBox-info").innerWidth();
    if (winWidth <= 768) {
        var totalHeight = $(window).height(); //页面整体高度
        $(".chatBox-info").css("height", totalHeight - topHeight);
        var infoHeight = $(".chatBox-info").innerHeight();//聊天头部以下高度
        //中间内容高度
        $(".chatBox-content").css("height", infoHeight - 45);
        $(".chatBox-activate").css("height", infoHeight - 45);

        $(".chatBox-list").css("height", totalHeight - topHeight);
        $(".div-textarea").css("width", winWidth - 45);
    } else {
        $(".chatBox-info").css("height", 550);
        $(".chatBox-content").css("height", 480);
        $(".chatBox-activate").css("height", 500);
        $(".chatBox-list").css("height", 500);
        $(".div-textarea").css("width", chatWidth - 45);
    }
}


function sendMessage() {
    var textContent = $(".div-textarea").html().replace(/[\n\r]/g, '<br>')
    if (textContent != "") {
        $(".chatBox-activate").append(
            "<div class=\"clearfloat\">" +
            "<div class=\"right\">" +
            "<div class=\"chat-message\"> " + textContent + " </div> " +
            "<div class=\"chat-avatars\"><img src=\"img/head.ico\" alt=\"\"></div>" +
            "</div>" +
            "</div>");
        //发送后清空输入框
        $(".div-textarea").html("");
        //聊天框默认最底部
        $(document).ready(function () {
            $("#chatBox-activate").scrollTop($("#chatBox-activate")[0].scrollHeight);
        });

        // 发送请求
        url = "/api/chat?message=" + encodeURIComponent(textContent)
        $.ajax({
            type: "GET",
            url: url,
            timeout: 10000, //超时时间设置，单位毫秒
            success: function (result) {
                // alert(result)
                getMessage(result);
            },
            error: function (jqXHR) {
                console.log("Error: " + jqXHR.status);
            }
        });
    }
}

// 渲染html回复
function getMessage(result) {
    $(".chatBox-activate").append(
        "<div class=\"clearfloat\">" +
        "<div class=\"left\">" +
        "<div class=\"chat-avatars\"><img src=\"img/fIco.ico\" alt=\"\"></div>" +
        "<div class=\"chat-message\"> " + result + "</div>" +
        "</div>" +
        "</div>");
    //发送后清空输入框
    $(".div-textarea").html("");
    //聊天框默认最底部
    $(document).ready(function () {
        $("#chatBox-activate").scrollTop($("#chatBox-activate")[0].scrollHeight);
    });
}


function getTime() {
    var date = new Date();
    var seperator1 = "-";
    var seperator2 = ":";
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
        + " " + date.getHours() + seperator2 + date.getMinutes();
    return currentdate;
}