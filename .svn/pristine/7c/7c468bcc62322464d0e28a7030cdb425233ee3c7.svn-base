$(function () {
    var id_result = 0;
    function ree() {
        $('#auto_tag').val(id_result)
    }

   $(function () {
            var jsondata =json_data;
            var box = $('#click_sellect_item');
            for (i = 0; i < jsondata.length; i++) {
                if(0==i){
                    box.append("<select  class=\"select_data_tag\" id=\"form-field-select-" + i + "\" style=\"width: 15%;margin-right:5px;margin-top:5px\"> " +
                        "<option value=\"-3\">" +
                        "请选择------------</option></select>")
                }
                else{
                    box.append("<select  class=\"select_data_tag\" id=\"form-field-select-" + i + "\" style=\"width: 15%;margin-right:5px;margin-top:5px;\"> " +
                        "<option value=\"-3\">" +
                        "请选择------------</option></select>")
                }

                for (j = 0; j < jsondata[i][0].length; j++) {
                    var $html = "<option value=\"" + jsondata[i][0][j][0] + "\">" + jsondata[i][0][j][1] + "</option>"
                    $("#form-field-select-" + i).append($html)
                }
                $("#form-field-select-" + i).find("option[value=" + jsondata[i][1] + "]").attr("selected", true);
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
