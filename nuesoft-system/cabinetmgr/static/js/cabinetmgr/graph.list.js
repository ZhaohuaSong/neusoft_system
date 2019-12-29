var table_data = '';
var cont = '';
var id_tab = '';
function overShow() {
    $('#dbcontent').find('td').mouseover(function() {
        cont = $(this).text(); // 获取到内容
        id_tab = $(this).attr('id');
        var my_cont = $(this).text(); // 获取到内容
        var my_id_tab = $(this).attr('id');
        var on_state_date = '';
        var power_on_date = '';
        var down_power_date = '';
        var client_name = '';
        var tt = my_id_tab + '-' + my_id_tab;
        var showDiv = document.getElementById(tt);
        var reg2=/^(\d+\-\w\-\d+)/;
        var patt1 = my_cont.match(reg2)
        var patt = patt1[0]
        $.each(table_data, function (i, item) {
            for (j = 0; j < Object.keys(item).length; j++) {
                if (patt == item[j][0]) {
                    if (item[j][3] == null) {
                        on_state_date = '未上架'
                    } else {
                        on_state_date = item[j][3];
                    }
                    if (item[j][4] == null) {
                        power_on_date = '未加电'
                    } else {
                        power_on_date = item[j][4];
                    }
                    if (item[j][5] == null) {
                        down_power_date = '无'
                    } else {
                        down_power_date = item[j][5];
                    }
                    client_name = item[j][6];
                    break
                }
            }
        });
        showDiv.style.left = event.clientX;
        showDiv.style.top = event.clientY;
        showDiv.style.display = 'block';
        showDiv.innerHTML = '客户：' + client_name + '<br>' + '首次上架日期：' + on_state_date + '<br>' + '首次加电日期：' + power_on_date + '<br>' + '下电日期： ' + down_power_date
    });
}
function outHide() {
    var on_state_date = '';
    var power_on_date = '';
    var down_power_date = '';
    var showDiv = document.getElementById(id_tab + '-' + id_tab);
    showDiv.style.display = 'none';
    showDiv.innerHTML = '';
}
jQuery(function ($) {

    /*
     树形菜单+检索
     */
    $('#treeview1').treeview({
        data: defaultData,
        //levels: 2,
        //showTags: true,
        onNodeSelected: function (event, node) {
            $.ajax({
                url: FILE_CONTENTS_LIST_URL,
                type: "POST",
                "data": {"id": node.id, "table_name": node.text},
                //"data": {"room_id": node.room_id, "building_id": node.building_id, "industry_id": industry_id, "table_name": node.text},
                success: function (result) {
                    $("#dbcontent").html('');
                    var jsonObj=eval(result);
                    var kobe = 0;
                    table_data = jsonObj;
                    $.each(jsonObj, function (i, item) {
                        var tds= '';
                        var j = 0;
                        for (j = 0; j < Object.keys(item).length; j++) {
                            if (item[j][1] == 10) {
                                tds = tds + ('<td id='+ item[j][0] +'onmouseover="overShow()" onmouseout="outHide()" align="center"  valign="middle" style="background-color:#FF6699 ">'
                                //+ '<a class="black" href="/cabinetmgr/networkdevice/list/' + item[j][2] + '">'
                                + item[j][0] +'</a>'
                                +'<div id='+ item[j][0] + '-' + item[j][0] +' style="position: absolute; background-color: white; border: 1px solid black;"></div>'
                                +'</td>'
                                )
                            }
                            else if (item[j][1] == 40 || item[j][1] == 44){
                                tds = tds + ('<td id='+ item[j][0] +' onmouseover="overShow()" onmouseout="outHide()" align="center"  valign="middle" style="background-color:#66CCFF" >'
                                //+ '<a class="black" href="/cabinetmgr/networkdevice/list/' + item[j][2] + '">'
                                + item[j][0] +'</a>'
                                +'<div id='+ item[j][0] + '-' + item[j][0] + '  style="position: absolute; background-color: white; border: 1px solid black;"></div>'
                                +'</td>'
                                )
                            }
                            else if (item[j][1] == 50) {
                                tds = tds + ('<td id='+ item[j][0] +' onmouseover="overShow()" onmouseout="outHide()" align="center"  valign="middle" style="background-color:#66FF33">'
                                //+ '<a class="black" href="/cabinetmgr/networkdevice/list/' + item[j][2] + '">'
                                + item[j][0] +'</a>'
                                +'<div id='+ item[j][0] + '-' + item[j][0] +' style="position: absolute; background-color: white; border: 1px solid black;"></div>'
                                +'</td>'
                                )
                            }
                            else if (item[j][1] == 23) {
                                tds = tds + ('<td id='+ item[j][0] +' onmouseover="overShow()" onmouseout="outHide()" align="center"  valign="middle" style="background-color:gray">'
                                    //+ '<a class="black" href="/cabinetmgr/networkdevice/list/' + item[j][2] + '">'
                                    + item[j][0] +'</a>'
                                    +'<div id='+ item[j][0] + '-' + item[j][0] +' style="position: absolute; background-color: white; border: 1px solid black;"></div>'
                                    +'</td>'
                                    )
                            }
                            else if (item[j][1] == 13) {
                                tds = tds + ('<td id='+ item[j][0] +' onmouseover="overShow()" onmouseout="outHide()" align="center"  valign="middle" style="background-color:yellow">'
                                    //+ '<a class="black" href="/cabinetmgr/networkdevice/list/' + item[j][2] + '">'
                                    + item[j][0] +'</a>'
                                    +'<div id='+ item[j][0] + '-' + item[j][0] +' style="position: absolute; background-color: white; border: 1px solid black;"></div>'
                                    +'</td>'
                                    )
                            }
                            else if (item[j][1] == 64) {
                                tds = tds + ('<td id='+ item[j][0] +' onmouseover="overShow()" onmouseout="outHide()" align="center"  valign="middle" style="background-color:white">'
                                    + '<a class="black" href="/cabinetmgr/networkdevice/list/' + item[j][2] + '">'
                                    + item[j][0] +'</a>'
                                    +'<div id='+ item[j][0] + '-' + item[j][0] +' style="position: absolute; background-color: white; border: 1px solid black;"></div>'
                                    +'</td>'
                                    )
                            }
                            else {
                                tds = tds + ('<td id='+ item[j][0] +' onmouseover="overShow()" onmouseout="outHide()" align="center"  valign="middle">'
                                    + '<a class="black"  ">'
                                    + item[j][0] +'</a>'
                                    +'<div id='+ item[j][0] + '-' + item[j][0] +' style="position: absolute; background-color: white; border: 1px solid black;"></div>'
                                    +'</td>'
                                    )
                            }
                        }
                        $("#dbcontent").append(
                            '<tr>' +
                            tds+
                            '</tr>'
                        );
                    });

                }
            });

        }
    })

    })
