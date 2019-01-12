$(document).ready(function () {
    $(".card").each(function () {
        var id = $(this).attr("id");
        var title = $(this).children("h6");
        var title_text = $(this).children("h6").text();
        $.post("/activity/get_activity_record", {"id": id}, function (data) {
            if (data.join == "yes") {
                title.append("<span class=\"badge badge-danger \" style=\"display: inline\">你已参加此活动</span>");
            } else {

            }
        })
    });

    /* 点击某一行显示修改和删除按钮 */
    $(".card").click(function () {
        if ($(this).children("h6").text().search("你已参加此活动") == -1) {
            action = "join"
        } else {
            $("#prompt").text("请确认是否退出此活动")
            $("#submit").text("退出");
            action = "quit"
        }
        $('#modal').modal();
        target_id = $(this).attr("id");
        console.log(action);
    });

    $("#submit").click(function (event) {
        event.preventDefault();
        var csrf_token = $("[name='csrfmiddlewaretoken']").val();
        var data = {
            "target_id": target_id,
            "action":action,
            "csrfmiddlewaretoken": csrf_token,
        }
        $.post("/activity/joinActivity", data, function (data) {
            document.write(data);
        })
    })
});