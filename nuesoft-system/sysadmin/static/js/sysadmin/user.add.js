$(function () {
    var id_result = 0;
    function ree() {
        $('#auto_tag').val(id_result)
    }

    $(function () {
        var list_all_info = json_data;
        var box = $('#click_sellect_item');
        if (list_all_info.length == 0) {
            box.append("<select  class=\"select_data_tag\" id=\"form-field-select-" + i + "\" style=\"width: 15%;margin-right:5px;margin-top:5px\"> " +
                "<option value=\"-3\">" +
                "请选择------------</option></select>")
        }

        for (i = 0; i < list_all_info.length; i++) {
            var select; //定义下拉框对象
            if (0 == i) {
                select = jQuery("<select  class=\"select_data_tag\" id=\"form-field-select-" + i + "\" style=\"width: 15%;margin-right:5px;margin-top:5px\"> " +
                    "<option value=\"-3\">" +
                    "请选择------------</option></select>")
            }
            else {
                select = jQuery("<select  class=\"select_data_tag\" id=\"form-field-select-" + i + "\" style=\"width: 15%;margin-right:5px;margin-top:5px\"> " +
                    "<option value=\"-3\">" +
                    "请选择------------</option></select>")
            }

            for (j = 0; j < list_all_info[i][0].length; j++) {
                var $html = "<option value=\"" + list_all_info[i][0][j][0] + "\">" + list_all_info[i][0][j][1] + "</option>"
                select.append($html)
            }
            select.find("option[value=" + list_all_info[i][1] + "]").attr("selected", true);

            box.append(select);
        }
    })
    //
    //
    //
    $(document).on("change", '.select_data_tag', function () {
        var id = $(this).attr('id');
        var num = id.charAt(id.length - 1);
        var select_num_tag = parseInt(num) + 1;
        var productId = $('#' + id).val()
        id_result = productId;
        ree()
        var num_list = new Array();
        $('.select_data_tag').each(function (i) {
            var id_list = $(this).attr("id");
            num_list[i] = id_list;
        });
        var numaa = num_list.length;
        for (i = 0; i < num_list.length; i++) {
            var nums = num_list[i].charAt(num_list[i].length - 1)
            if (nums > num) {
                $("#" + num_list[i]).remove()
            }
        }
        if (productId == "请选择") {

        } else {
            $.ajax({
                type: 'POST',
                url: url_org_list,
                data: {"parent_id": productId, "tag": 0},
                success: function (data) {
                    var select_data_list = data['select_data_list']
                    $('#click_sellect_item').append("<select  class=\"select_data_tag\" id=\"form-field-select-" + select_num_tag + "\" style=\"width: 15%;margin-right:5px;margin-top:5px\"> " +
                        "<option value=\"请选择\">" +
                        "请选择------------</option> </select>")

                    for (var i = 0; i < select_data_list.length; i++) {
                        var $html = "<option value=\"" + select_data_list[i][0] + "\">" + select_data_list[i][1] + "</option>"
                        $("#form-field-select-" + select_num_tag).append($html)
                    }
                    if (select_data_list.length == 0) {
                        $("#form-field-select-" + select_num_tag).remove()
                    }
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log("error");
                },
                dataType: 'json'
            });
        }
    })


})
