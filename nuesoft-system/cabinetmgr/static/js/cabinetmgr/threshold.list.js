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

            console.info(ajax);
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
    var pospDataTable = $('#dynamic-table').DataTable({
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
                "url": TXNNAMES_LIST_URL,
                "type": "GET",

            },
            lengthMenu: [ // 最多查询数量限制 50
                [10, 25, 50],
                ['10', '25', '50']
            ],
            columnDefs: [ // 设置第二列居中
                {
                    orderable: true,
                    searchable: true,
                    className: "center",
                    targets: [1]
                },
                {
                    orderable: false,
                    searchable: false,
                    className: "center",
                    targets: [-1]
                },
            ],
            "language": {
                "processing": "进度君正在努力的加载.... "
            },
                //
            //"fnRowCallback": function (nRow, aData, iDataIndex) {
            //    $('td:eq(-1)', nRow).html('<div class="hidden-sm hidden-xs action-buttons"> '
            //        + '<a class="green" href="dialingtest/' + aData[0] + '">'
            //        + '<i class="ace-icon fa fa-pencil bigger-130"></i>'
            //        + ' 拨测</a>'
            //        + '</div>'
            //        + '<div class="hidden-md hidden-lg">'
            //        + '<div class="inline pos-rel">'
            //        + '<button class="btn btn-minier btn-yellow dropdown-toggle" data-toggle="dropdown" data-position="auto">'
            //        + '<i class="ace-icon fa fa-caret-down icon-only bigger-120"></i>'
            //        + '</button>'
            //        + '<ul class="dropdown-menu dropdown-only-icon dropdown-yellow dropdown-menu-right dropdown-caret dropdown-close">'
            //        + '<li><a href="dialingtest/' + aData[0] + '" class="tooltip-success" data-rel="tooltip" title="" data-original-title="Edit">'
            //        + '<span class="green">'
            //        + '<i class="ace-icon fa fa-pencil-square-o bigger-120"></i>'
            //        + '</span></a></li></ul></div></div>'
            //    );
            //    return nRow;
            //},
            //
            "fnDrawCallback": function () {
                var api = this.api();
                var startIndex = api.context[0]._iDisplayStart;
                api.column(1).nodes().each(function (cell, i) {
                    cell.innerHTML = startIndex + i + 1;
                });
                buttonsDisable(); //禁用新增、删除
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
                //null,
            ],
            //"dom": '<lf<t>ip>'  , //清除表格头部、底部 样式
            select: { //多行选择
                style: 'multi'
            }
        })
        ;

    // 禁用 修改 、删除
    //
    function buttonsDisable() {
        $("#btn-update").attr("disabled", 'disabled');
        $("#btn-delete").attr("disabled", 'disabled');
    }

    // 启用 修改 、删除
    //
    function buttonsEnable() {
        $("#btn-update").removeAttr("disabled");
        $("#btn-delete").removeAttr("disabled");
    }


    // 新增、删除按钮启用、禁用的监听事件
    //
    pospDataTable.on('click', 'tr', function () {
        //$(this).toggleClass('selected');
        var datas = pospDataTable.rows('.selected').data()
        if (datas.length > 0) {
            buttonsEnable()
        } else {
            buttonsDisable()
        }
    });


    /////////////////////////////////
    // datatools
    $.fn.dataTable.Buttons.defaults.dom.container.className = 'dt-buttons btn-overlap btn-group btn-overlap';

    new $.fn.dataTable.Buttons(pospDataTable, {
        buttons: [
            {
                "extend": "colvis",
                "text": "<i class='fa fa-search bigger-110 blue'></i> <span class='hidden'>Show/hide columns</span>",
                "className": "btn btn-white btn-primary btn-bold",
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
            //{
            //    "extend": "pdf",
            //    "text": "<i class='fa fa-file-pdf-o bigger-110 red'></i> <span class='hidden'>Export to PDF</span>",
            //    "className": "btn btn-white btn-primary btn-bold"
            //},
            {
                "extend": "print",
                "text": "<i class='fa fa-print bigger-110 grey'></i> <span class='hidden'>Print</span>",
                "className": "btn btn-white btn-primary btn-bold",
                autoPrint: false,
                message: 'This print was produced using the Print button for DataTables'
            }
        ]
    });

    //setTimeout(function () {
    //    $($('.tableTools-container')).find('a.dt-button').each(function () {
    //        var div = $(this).find(' > div').first();
    //        if (div.length == 1) div.tooltip({container: 'body', title: div.parent().text()});
    //        else $(this).tooltip({container: 'body', title: $(this).text()});
    //    });
    //}, 500);

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
    $('#dynamic-table > thead > tr > th input[type=checkbox], #dynamic-table_wrapper input[type=checkbox]').eq(0).on('click', function () {
        var th_checked = this.checked;//checkbox inside "TH" table header

        $('#dynamic-table').find('tbody > tr').each(function () {
            var row = this;
            if (th_checked) pospDataTable.row(row).select();
            else  pospDataTable.row(row).deselect();
        });
    });

    //select/deselect a row when the checkbox is checked/unchecked
    $('#dynamic-table').on('click', 'td input[type=checkbox]', function () {
        var row = $(this).closest('tr').get(0);
        if (this.checked) pospDataTable.row(row).deselect();
        else pospDataTable.row(row).select();
    });

    $('#dynamic-table').on('click', 'td input[type=button]', function () {
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


// 通用的删除方法
//
    $("#btn-delete").bind("click",
        function () {
            var datas = pospDataTable.rows('.selected').data()
            var ids = [];
            var json_data = {};
            for (var i = 0; i < datas.length; i++) {
                ids.push(datas[i][0])
            }
            if (ids == 0) {
                var dialog = $("#dialog-message-null").removeClass('hide').dialog({
                    modal: true,
                    title: "操作提示：",
                    title_html: true,
                    buttons: [
                        {
                            text: "确定",
                            "class": "btn btn-primary btn-minier",
                            click: function () {
                                $(this).dialog("close");
                            }
                        }
                    ]
                });
            } else {
                json_data['ids'] = ids;
                var postdata = JSON.stringify(json_data);
                var dialog = $("#dialog-message").removeClass('hide').dialog({
                    modal: true,
                    title: "操作提示：" + "数据总共（" + datas.length + "）条",
                    title_html: true,
                    buttons: [
                        {
                            text: "取消",
                            "class": "btn btn-minier",
                            click: function () {
                                $(this).dialog("close");
                            }
                        },
                        {
                            text: "确定",
                            "class": "btn btn-primary btn-minier",
                            click: function () {
                                $(this).dialog("close");
                                $.ajax({
                                    type: "GET",
                                    url: "delete",
                                    data: {ids: postdata},
                                    dataType: "json",
                                    success: function (data) {
                                        //TODO   修改删除 datatables 数据刷新问题
                                        pospDataTable.clearPipeline().draw();
                                    }
                                });
                            }
                        }
                    ]
                });
            }
        });
// 通用的更新方法
//
    $("#btn-update").bind("click",
        function () {
            var datas = pospDataTable.rows('.selected').data();
            var ids = [];
            var json_data = {};
            for (var i = 0; i < datas.length; i++) {
                ids.push(datas[i][0])
            }
            if (ids == 0) {
                var dialog = $("#dialog-message-update").removeClass('hide').dialog({
                    modal: true,
                    title: "操作提示：",
                    title_html: true,
                    buttons: [
                        {
                            text: "确定",
                            "class": "btn btn-primary btn-minier",
                            click: function () {
                                $(this).dialog("close");
                            }
                        }
                    ]
                });
            } else {
                window.location.href = "edit/" + ids[0]
            }
        });

// 通用的新增方法
    $("#btn-add").bind("click",
        function () {
            current_page = pospDataTable.page()
            //alert(current_page)
            window.location.href = "add"
        });

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
    $("#btn-search").click(function (d) {
            var args1 = $("#in-search").val();
            $('#sech_item').attr('role', '')
            $('#sech_item').attr('role', d.resource_id)
            console.info(d.resource_id)
            //var args2 = $("#input2").val();
            //用空格隔开，达到多条件搜索的效果，相当于两个关键字
            pospDataTable.search(args1).draw();
            //table.search(args1+" "+args2).draw(false);//保留分页，排序状态
        }
    );

    //监听输入的回车事件
    //
    $('#in-search').bind('keypress', function (event) {
        if (event.keyCode == "13") {
            pospDataTable.search($('#in-search').val()).draw();
        }
    });

    // 隐藏搜索
    //
    $("#dynamic-table_filter").hide();

})
