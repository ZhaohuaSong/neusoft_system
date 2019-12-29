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
                "data": {"id": node.id, "file_name": node.text},
                success: function (result) {
                    //console.info(node)
                    //console.info(result)
                    $("#dbcontent").html('')
                    var jsonObj=eval(result);
                        //console.info(jsonObj)

                    var kobe = 0;

                    $.each(jsonObj, function (i, item) {
                        //console.info(item)
                        for(var key in item){
                            //console.info(key);
                            kobe = key;
                        }
                        if (kobe == "page_num") {
                                return false
                        }
                        var tds= ''
                        var j = 0;
                        for (j = 0; j <= kobe; j++) {
                            tds += ('<td style="word-break:break-all" align="center"  valign="middle">'+item[j]+'</td>')
                        }
                        //console.info(tds)

                        $("#dbcontent").append(
                            '<tr>' +
                            //'<td><input type="checkbox"></td>' +
                            tds +
                            '</tr>'
                        )
                    });
                }
            });

        },
    });
});
