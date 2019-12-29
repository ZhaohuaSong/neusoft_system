jQuery(function ($) {
//
// Pipelining function for DataTables. To be used to the `ajax` option of DataTable
//  管道式分页加载数据，减少ajax请求
//

    $.fn.dataTable.pipeline = function (opts) {
        // Configuration options
        var conf = $.extend({
            pages: 5,     // number of pages to cache 缓存页面数量
            url: '',      // script url  脚本url
            data: null,   // function or object with parameters to send to the server
                          // matching how `ajax.data` works in DataTables
            method: 'GET' // Ajax HTTP method type
        }, opts);

        // Private variables for storing the cache
        var cacheLower = -1;
        var cacheUpper = null;
        var cacheLastRequest = null;
        var cacheLastJson = null;

        return function (request, drawCallback, settings) {
            var ajax = false;
            var requestStart = request.start;
            var drawStart = request.start;
            var requestLength = request.length;
            var requestEnd = requestStart + requestLength;

            if (settings.clearCache) {
                // API requested that the cache be cleared
                // 注册
                ajax = true;
                settings.clearCache = false;
            }
            else if (cacheLower < 0 || requestStart < cacheLower || requestEnd > cacheUpper) {
                // outside cached data - need to make a request
                ajax = true;
            }
            else if (JSON.stringify(request.order) !== JSON.stringify(cacheLastRequest.order) ||
                JSON.stringify(request.columns) !== JSON.stringify(cacheLastRequest.columns) ||
                JSON.stringify(request.search) !== JSON.stringify(cacheLastRequest.search)
            ) {
                // properties changed (ordering, columns, searching)
                ajax = true;
            }
            // Store the request for checking next time around
            cacheLastRequest = $.extend(true, {}, request);

            if (ajax) {
                // Need data from the server
                if (requestStart < cacheLower) {
                    requestStart = requestStart - (requestLength * (conf.pages - 1));

                    if (requestStart < 0) {
                        requestStart = 0;
                    }
                }
                cacheLower = requestStart;
                cacheUpper = requestStart + (requestLength * conf.pages);

                request.start = requestStart;
                request.length = requestLength * conf.pages;

                // Provide the same `data` options as DataTables.
                if ($.isFunction(conf.data)) {
                    // As a function it is executed with the data object as an arg
                    // for manipulation. If an object is returned, it is used as the
                    // data object to submit
                    var d = conf.data(request);
                    if (d) {
                        $.extend(request, d);
                    }
                }
                else if ($.isPlainObject(conf.data)) {
                    // As an object, the data given extends the default
                    $.extend(request, conf.data);
                }

                settings.jqXHR = $.ajax({
                    "type": conf.method,
                    "url": conf.url,
                    "data": request,
                    "dataType": "json",
                    "cache": false,
                    "success": function (json) {
                        cacheLastJson = $.extend(true, {}, json);

                        if (cacheLower != drawStart) {
                            json.data.splice(0, drawStart - cacheLower);
                        }
                        if (requestLength >= -1) {
                            json.data.splice(requestLength, json.data.length);
                        }

                        drawCallback(json);
                    }
                });
            }
            else {
                json = $.extend(true, {}, cacheLastJson);
                json.draw = request.draw; // Update the echo for each response
                json.data.splice(0, requestStart - cacheLower);
                json.data.splice(requestLength, json.data.length);

                drawCallback(json);
            }
        }
    };

// Register an API method that will empty the pipelined data, forcing an Ajax
// fetch on the next draw (i.e. `table.clearPipeline().draw()`)
//
// 给datables 注册一个API方法，将空的数据，强制让Ajax 取下往上
//（即`表。clearpipeline()。draw() `）
    $.fn.dataTable.Api.register('clearPipeline()', function () {
        return this.iterator('table', function (settings) {
            settings.clearCache = true;
        });
    });

//
// DataTables initialisation
//  Datatables 初始化页面 关键绑定 ID (dynamic-table)
    cru_url = window.location.pathname;
    first_url = "/zabbixmgr/analysis/list";
    if (cru_url.indexOf(first_url) >= 0) {
        var tab_url = [TXNNAMES_LIST_URL, TABPAGE_LIST_URL];
        var table_name = ['#dynamic-table', '#dynamic-table_1'];
    } else {
        table_id = cru_url.match(/(\w+)\/\d+\/\d+\/\d+$/);
        if ( table_id[1] === 'a') {
            var tab_url = [TXNNAMES_LIST_URL, TABPAGE_LIST_URL];
            var table_name = ['#dynamic-table', '#dynamic-table_1'];

        } else {
            var tab_url = [TXNNAMES_LIST_URL];
            var table_name = ['#dynamic-table'];
        }
    }

    $.each(table_name,function(i){
    var pospDataTable = $(table_name[i]).DataTable({
            "processing": true,
            "serverSide": true,
            "searching": true,
            "order": [[1, "asc"]], //默认排序从第几行
            "autoWidth": false,
            //"ajax": $.fn.dataTable.pipeline({
            //    url: TXNNAMES_LIST_URL,
            //    pages: 5 // number of pages to cache
            //}),
            //"ajax": TXNNAMES_LIST_URL,
            "ajax": {
                "url": tab_url[i],
                "type": "GET"
            },
            lengthMenu: [ // 最多查询数量限制 50
                [10, 25, 500],
                ['10', '25', '500']
            ],
            columnDefs: [ // 设置第二列居中
                {
                    orderable: true,
                    searchable: true,
                    className: "center",
                    targets: [1]
                },
                {
                    orderable: true,
                    searchable: true,
                    className: "center",
                    targets: [-1]
                }
            ],
            "language": {
                "processing": "进度君正在努力的加载.... "
            },

            "fnDrawCallback": function () {
                var api = this.api();
                var startIndex = api.context[0]._iDisplayStart;
                api.column(1).nodes().each(function (cell, i) {
                    cell.innerHTML = startIndex + i + 1;
                });
                //buttonsDisable(); //禁用新增、删除
            }
            ,
            "aoColumns": [
                {
                    "sClass": "text-center",
                    "data": "id",
                    "render": function (data, type, full, meta) {
                        return '<label class="pos-rel"> <input type="checkbox" value="' + data + '" class="ace" /> <span class="lbl"></span> </label> '
                    },
                    "bSortable": false
                },
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null
            ],
            //"dom": '<lf<t>ip>'  , //清除表格头部、底部 样式
            select: { //多行选择
                style: 'multi'
            }
        });

    /////////////////////////////////
    // datatools
    if (tab_url[i] === TXNNAMES_LIST_URL) {
        $.fn.dataTable.Buttons.defaults.dom.container.className = 'dt-buttons btn-overlap btn-group btn-overlap';
        new $.fn.dataTable.Buttons(pospDataTable, {
            buttons: [
                {
                    "extend": "colvis",
                    "text": "<i class='fa fa-search bigger-110 blue'></i> <span class='hidden'>Show/hide columns</span>",
                    "className": "btn btn-white btn-primary btn-bold"
                },
                {
                    "extend": "copy",
                    "text": "<i class='fa fa-copy bigger-110 pink'></i> <span class='hidden'>Copy to clipboard</span>",
                    "className": "btn btn-white btn-primary btn-bold"
                },
                {
                    "extend": "csv",
                    "text": "<i class='fa fa-database bigger-110 orange'></i> <span class='hidden'>Export to CSV</span>",
                    "className": "btn btn-white btn-primary btn-bold"
                },
                {
                    "extend": "excel",
                    "text": "<i class='fa fa-file-excel-o bigger-110 green'></i> <span class='hidden'>Export to Excel</span>",
                    "className": "btn btn-white btn-primary btn-bold"
                },
                {
                    "extend": "print",
                    "text": "<i class='fa fa-print bigger-110 grey'></i> <span class='hidden'>Print</span>",
                    "className": "btn btn-white btn-primary btn-bold",
                    autoPrint: false,
                    message: 'This print was produced using the Print button for DataTables'
                }
            ]
        });
    }
    //setTimeout(function () {
    //    $($('.tableTools-container')).find('a.dt-button').each(function () {
    //        var div = $(this).find(' > div').first();
    //        if (div.length == 1) div.tooltip({container: 'body', title: div.parent().text()});
    //        else $(this).tooltip({container: 'body', title: $(this).text()});
    //    });
    //}, 500);
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    pospDataTable.buttons().container().appendTo($('.tableTools-container'));

    //style the message box 复制 checkbox
    var defaultCopyAction = pospDataTable.button(1).action();
    pospDataTable.button(1).action(function (e, dt, button, config) {
        defaultCopyAction(e, dt, button, config);
        $('.dt-button-info').addClass('gritter-item-wrapper gritter-info gritter-center white');
    });


    var defaultColvisAction = pospDataTable.button(0).action();
    pospDataTable.button(0).action(function (e, dt, button, config) {
        defaultColvisAction(e, dt, button, config);


        if ($('.dt-button-collection > .dropdown-menu').length == 0) {
            $('.dt-button-collection')
                .wrapInner('<ul class="dropdown-menu dropdown-light dropdown-caret dropdown-caret" />')
                .find('a').attr('href', '#').wrap("<li />")
        }
        $('.dt-button-collection').appendTo('.tableTools-container .dt-buttons')
    });

    pospDataTable.on('select', function (e, dt, type, index) {
        if (type === 'row') {
            $(pospDataTable.row(index).node()).find('input:checkbox').prop('checked', true);
        }
    });
    pospDataTable.on('deselect', function (e, dt, type, index) {
        if (type === 'row') {
            $(pospDataTable.row(index).node()).find('input:checkbox').prop('checked', false);
        }
    });

    /////////////////////////////////
    //table checkboxes
    $('th input[type=checkbox], td input[type=checkbox]').prop('checked', false);

    //select/deselect all rows according to table header checkbox
    $(table_name[i]+' > thead > tr > th input[type=checkbox], '+ table_name[i] + '_wrapper input[type=checkbox]').eq(0).on('click', function () {
        var th_checked = this.checked;//checkbox inside "TH" table header

        $(table_name[i]).find('tbody > tr').each(function () {
            var row = this;
            if (th_checked) pospDataTable.row(row).select();
            else  pospDataTable.row(row).deselect();
        });
    });

    //select/deselect a row when the checkbox is checked/unchecked
    $(table_name[i]).on('click', 'td input[type=checkbox]', function () {
        var row = $(this).closest('tr').get(0);
        if (this.checked) pospDataTable.row(row).deselect();
        else pospDataTable.row(row).select();
    });

    $(table_name[i]).on('click', 'td input[type=button]', function () {
        //var row = $(this).closest('tr').get(0);
        //if (this.checked) pospDataTable.row(row).deselect();
        //else pospDataTable.row(row).select();
        alert("test")
    });

    //$(document).on('click', '#dynamic-table .dropdown-toggle', function (e) {
    //    e.stopImmediatePropagation();
    //    e.stopPropagation();
    //    e.preventDefault();
    //});

    /********************************/
    //add tooltip for small view action buttons in dropdown menu
    $('[data-rel="tooltip"]').tooltip({placement: tooltip_placement});

    //tooltip placement on right or left
    function tooltip_placement(context, source) {
        var $source = $(source);
        var $parent = $source.closest('table')
        var off1 = $parent.offset();
        var w1 = $parent.width();

        var off2 = $source.offset();
        //var w2 = $source.width();

        if (parseInt(off2.left) < parseInt(off1.left) + parseInt(w1 / 2)) return 'right';
        return 'left';
    }

//////////////////////////////////////////////////////////////////////////////////////////

// 查询方法
        $("#btn-traffic_search").bind("click",
            function () {
                current_page = pospDataTable.page();
                var args1 = $("#in-search").val(); //时间粒度
                var args2 = $("#in-search_1").val(); //始时间
                var args3 = $("#in-search_2").val(); //止时间
                var makeupCo = $("#makeupCo").val(); //用户
                var makeupCo_1 = $("#makeupCo_1").val(); //端口
                if (makeupCo.length === 0) {
                    alert('用户不能为空！');
                    return
                } else {
                    var f = 0;
                    for (var key in group_dict) {
                        if (makeupCo === group_dict[key]) {
                            makeupCo = key;
                            f = 1;
                            break
                        }
                    }
                    if (f === 0) {
                        alert('用户名错误！');
                        return
                    }
                }

                if (makeupCo_1.length === 0) {
                    makeupCo_1 = 'a'
                } else {
                    var f2 = 0;
                    for (var key_2 in port_dict) {
                        if (makeupCo_1 === port_dict[key_2]) {
                            makeupCo_1 = key_2;
                            f2 = 1;
                            break
                        }
                    }
                    if (f2 === 0) {
                        alert('端口不存在！');
                        return
                    }
                }


                var begindate = new Date(args2.replace(/\-/g, "\/"));
                begindate = begindate.toLocaleDateString();
                begindate =Date.parse(begindate)/1000;

                var lastdate = new Date(args3.replace(/\-/g, "\/"));
                lastdate = lastdate.toLocaleDateString();
                lastdate =Date.parse(lastdate)/1000;

                var myDate = new Date();
                var nowdate = myDate.toLocaleDateString();
                nowdate = Date.parse(nowdate)/1000;
                if ((nowdate - begindate) > 63158400) { //两年
                    alert('请选择两年内时间！');
                    return
                } else if ((lastdate - begindate) > 518400) {
                    if (args1 == '1分钟' || args1 == '5分钟') {
                        alert('抱歉，时间范围大于6天时间粒度只可选1小时或1天！')
                        return
                    }
                }

                var test = window.location.href;
                args2 = args2.match(/(\d+)/g);
                args3 = args3.match(/(\d+)/g);
                args2 = args2[0]+args2[1]+args2[2];
                args3 = args3[0]+args3[1]+args3[2];
                if (args1 === '1分钟') {
                    args1 = '1'
                } else if (args1 === '5分钟') {
                    args1 = '2'
                } else if (args1 === '10分钟') {
                    args1 = '5'
                } else if (args1 === '1小时') {
                    args1 = '3'
                } else if (args1 === '1天') {
                    args1 = '4'
                } else {
                    alert('时间粒度错误，请选择正确的时间粒度!');
                    return;
                }
                t = test.match(/(\w+\:\/\/\d+\.\d+\.\d+\.\d+\:\d+\/zabbixmgr)/g)[0];
                var arg = t + '/trafficdata/list/' + makeupCo + '/' + makeupCo_1 + '/' + args2 + '/' + args3 + '/' + args1 + '/' + industry_id;
                window.location.href = arg
            });
    //}


    // 右边的悬浮控件
    $(".ace-settings-btn").click(function () {
            if ($(".ace-settings-btn").attr("class").indexOf("open") > 0) {
                $(".ace-settings-btn").removeClass("open");
            } else {
                $(".ace-settings-btn").addClass("open");
            }
            if ($(".ace-settings-box").attr("class").indexOf("open") > 0) {
                $(".ace-settings-box").removeClass("open");
            } else {
                $(".ace-settings-box").addClass("open");
            }
        }
    );

    // 监听点击事件
    //$("#btn-in-search").click(function () {
    //        var args1 = $("#in-search_1").val();
    //        //var args2 = $("#input2").val();
    //        //用空格隔开，达到多条件搜索的效果，相当于两个关键字
    //        pospDataTable.search(args1).draw();
    //        //table.search(args1+" "+args2).draw(false);//保留分页，排序状态
    //    }
    //);

    //tab页端口查询监听事件
    if (tab_url[i] === TABPAGE_LIST_URL) {
        $("#tab-btn-search").bind("click",
            function () {
                var search_val = $('#tab-in-search').val();
                if (search_val === '1天') {
                    search_val = 1
                } else if (search_val === '7天') {
                    search_val = 7
                } else if (search_val === '1个月') {
                    search_val = 30
                } else if (search_val === '3个月') {
                    search_val = 90
                } else {
                    alert('请选择正确的时间粒度！')
                    return
                }
                pospDataTable.search(search_val).draw();
            });
        $('#tab-in-search').bind('keypress', function (event) {
        if (event.keyCode == "13") {
            pospDataTable.search($('#tab-in-search').val()).draw();
        }
        });
    }


    // 隐藏搜索
    //
    $("#dynamic-table_filter").hide();
    $("#dynamic-table_1_filter").hide();
     })/////////////////////////////////////////////////////////////////
})
