jQuery(function ($) {

    /*
     树形菜单+检索
     */
    $('#treeview1').treeview({
        data: defaultData,
        //levels: 1,
        //showTags: true,
        onNodeSelected: function (event, node) {
            $.ajax({
                url: FILE_CONTENTS_LIST_URL,
                type: "POST",
                "data": {"id": node.id, "table_name": node.text},
                success: function (result) {
                    //console.info(node)
                    //console.info(result.length)
                    $("#dbcontent").html('')
                    //console.info('vvvvvvvvv')
                    var jsonObj=eval(result);
                    //console.info('kkkkk')
                    //console.info(jsonObj)
                    //
                    var kobe = 0;

                    $.each(jsonObj, function (i, item) {
                        //console.info(item)
                        //console.info(Object.keys(item).length)
                        for(var key in item){
                            //console.info(key);
                            kobe = key;
                        }
                        if (kobe == "page_num") {
                                return false
                        }
                        var tds= ''
                        var j = 0;
                        for (j = 0; j < Object.keys(item).length; j++) {
                            if (item[j][1] == 10) {
                                tds = tds + ('<td align="center"  valign="middle" style="background-color:red">' + item[j][0] + '</td>')
                            }
                            else if (item[j][1] == 40 || item[j][1] == 44){
                                tds = tds + ('<td align="center"  valign="middle" style="background-color:blue">' + item[j][0] + '</td>')
                            }
                            else if (item[j][1] == 50) {
                                tds = tds + ('<td align="center"  valign="middle" style="background-color:green">' + item[j][0] + '</td>')
                            }
                            else if (item[j][1] == 23) {
                                tds = tds + ('<td align="center"  valign="middle" style="background-color:gray">' + item[j][0] + '</td>')
                            }
                            else if (item[j][1] == 13) {
                                tds = tds + ('<td align="center"  valign="middle" style="background-color:yellow">' + item[j][0] + '</td>')
                            }
                            else {
                                tds = tds + ('<td align="center"  valign="middle">' + item[j][0] + '</td>')
                            }
                        }
                        //console.info(tds)

                        $("#dbcontent").append(
                            '<tr>' +
                            '<td><input type="checkbox"></td>' +
                            tds+
                            '</tr>'
                        )
                    });

                }
            });

        },
    });

    })
