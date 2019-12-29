jQuery(function ($) {


    // 树形结构重绘

    //function merchanttreedraw() {
    //    $("#tree1").removeData("fu.tree");
    //    $("#tree1").unbind('click.fu.tree');
    //    treedata = getTreeData('-1')
    //}


    $("#dynamic-table_filter").hide();

    $(document).on('click', '.tree-branch-header', function () {
        var id = $(this).find('#id_parent_node').text();
        $('#sech_item').attr('role', id)
        pospDataTable.search($('#in-search').val()).draw();
    })

    $(document).on('click', '#btn-search', function () {
        insearch = $('#in-search').val()
        if (insearch == null || insearch == '') {
            $('#sech_item').attr('role', '0')
        } else {
            aa = $('#sech_item').attr('role', '-11')
        }
        //merchanttreedraw();
        tree_search('treeDemo', 'name', $('#in-search').val())
    })

    var setting = {
        data: {
            simpleData: {
                enable: true
            }
        }
    };



    var zNodes = [
        {id: 1, pId: 0, name: "父节点1 - 展开", open: true},
        {id: 11, pId: 1, name: "父节点11 - 折叠"},
        {id: 111, pId: 11, name: "叶子节点111"},
        {id: 112, pId: 11, name: "叶子节点112"},
        {id: 113, pId: 11, name: "叶子节点113"},
        {id: 114, pId: 11, name: "叶子节点114"},
        {id: 12, pId: 1, name: "父节点12 - 折叠"},
        {id: 121, pId: 12, name: "叶子节点121"},
        {id: 122, pId: 12, name: "叶子节点122"},
        {id: 123, pId: 12, name: "叶子节点123"},
        {id: 124, pId: 12, name: "叶子节点124"},
        {id: 13, pId: 1, name: "父节点13 - 没有子节点", isParent: true},
        {id: 2, pId: 0, name: "父节点2 - 折叠"},
        {id: 21, pId: 2, name: "父节点21 - 展开", open: true},
        {id: 211, pId: 21, name: "叶子节点211"},
        {id: 212, pId: 21, name: "叶子节点212"},
        {id: 213, pId: 21, name: "叶子节点213"},
        {id: 214, pId: 21, name: "叶子节点214"},
        {id: 22, pId: 2, name: "父节点22 - 折叠"},
        {id: 221, pId: 22, name: "叶子节点221"},
        {id: 222, pId: 22, name: "叶子节点222"},
        {id: 223, pId: 22, name: "叶子节点223"},
        {id: 224, pId: 22, name: "叶子节点224"},
        {id: 23, pId: 2, name: "父节点23 - 折叠"},
        {id: 231, pId: 23, name: "叶子节点231"},
        {id: 232, pId: 23, name: "叶子节点232"},
        {id: 233, pId: 23, name: "叶子节点233"},
        {id: 234, pId: 23, name: "叶子节点234"},
        {id: 3, pId: 0, name: "父节点3 - 没有子节点", isParent: true}
    ];



   // $(document).ready(function () {

   //     $.fn.zTree.init($("#treeDemo"), setting, zNodes);

  //  });

    var demoMsg = {
        async: "正在进行异步加载，请等一会儿再点击...",
        expandAllOver: "全部展开完毕",
        asyncAllOver: "后台异步加载完毕",
        asyncAll: "已经异步加载完毕，不再重新加载",
        expandAll: "已经异步加载完毕"
    }
    var setting = {

        async: {
            enable: true,
            url: REMOTE_URL,
            autoParam: ["id", "name=n", "level=lv"],
            otherParam: {"otherParam": "zTreeAsyncTest"},
            dataFilter: filter,
            type: "get"
        },
        callback: {
            beforeAsync: beforeAsync,
            onAsyncSuccess: onAsyncSuccess,
            onAsyncError: onAsyncError,
            beforeClick: beforeClick,
            onClick: onClick
        },
        view: {
            showIcon: true,
            fontCss: getFontCss
        }
    };


    function filter(treeId, parentNode, childNodes) {
        if (!childNodes) return null;
        for (var i = 0, l = childNodes.length; i < l; i++) {
            childNodes[i].name = childNodes[i].name.replace(/\.n/g, '.');
        }
        return childNodes;
    }

    function beforeAsync() {
        curAsyncCount++;
    }

    function onAsyncSuccess(event, treeId, treeNode, msg) {
        curAsyncCount--;
        if (curStatus == "expand") {
            expandNodes(treeNode.children);
        } else if (curStatus == "async") {
            asyncNodes(treeNode.children);
        }

        if (curAsyncCount <= 0) {
            if (curStatus != "init" && curStatus != "") {
                $("#demoMsg").text((curStatus == "expand") ? demoMsg.expandAllOver : demoMsg.asyncAllOver);
                asyncForAll = true;
            }
            curStatus = "";
        }
        expandAll()
    }

    function onAsyncError(event, treeId, treeNode, XMLHttpRequest, textStatus, errorThrown) {
        curAsyncCount--;

        if (curAsyncCount <= 0) {
            curStatus = "";
            if (treeNode != null) asyncForAll = true;
        }
    }

    var curStatus = "init", curAsyncCount = 0, asyncForAll = false,
        goAsync = false;

    function expandAll() {
        if (!check()) {
            return;
        }
        var zTree = $.fn.zTree.getZTreeObj("treeDemo");
        if (asyncForAll) {
            $("#demoMsg").text(demoMsg.expandAll);
            zTree.expandAll(true);
        } else {
            expandNodes(zTree.getNodes());
            if (!goAsync) {
                $("#demoMsg").text(demoMsg.expandAll);
                curStatus = "";
            }
        }
    }

    function expandNodes(nodes) {
        if (!nodes) return;
        curStatus = "expand";
        var zTree = $.fn.zTree.getZTreeObj("treeDemo");
        for (var i = 0, l = nodes.length; i < l; i++) {
            zTree.expandNode(nodes[i], true, false, false);
            if (nodes[i].isParent && nodes[i].zAsync) {
                expandNodes(nodes[i].children);
            } else {
                goAsync = true;
            }
        }
    }

    function asyncAll() {
        if (!check()) {
            return;
        }
        var zTree = $.fn.zTree.getZTreeObj("treeDemo");
        if (asyncForAll) {
            $("#demoMsg").text(demoMsg.asyncAll);
        } else {
            asyncNodes(zTree.getNodes());
            if (!goAsync) {
                $("#demoMsg").text(demoMsg.asyncAll);
                curStatus = "";
            }
        }
    }

    function asyncNodes(nodes) {
        if (!nodes) return;
        curStatus = "async";
        var zTree = $.fn.zTree.getZTreeObj("treeDemo");
        for (var i = 0, l = nodes.length; i < l; i++) {
            if (nodes[i].isParent && nodes[i].zAsync) {
                asyncNodes(nodes[i].children);
            } else {
                goAsync = true;
                zTree.reAsyncChildNodes(nodes[i], "refresh", true);
            }
        }
    }

    function reset() {
        if (!check()) {
            return;
        }
        asyncForAll = false;
        goAsync = false;
        $("#demoMsg").text("");
        $.fn.zTree.init($("#treeDemo"), setting);
    }

    function check() {
        if (curAsyncCount > 0) {
            $("#demoMsg").text(demoMsg.async);
            return false;
        }
        return true;
    }

   // $(document).ready(function () {

        $.fn.zTree.init($("#treeDemo"), setting);
        //$("#expandAllBtn").bind("click", expandAll);
        //$("#asyncAllBtn").bind("click", asyncAll);
        //$("#resetBtn").bind("click", reset);
   // });

    var log, className = "dark";

    function beforeClick(treeId, treeNode, clickFlag) {
        return (treeNode.click != false);
    }

    function onClick(event, treeId, treeNode, clickFlag) {
        $('#sech_item').attr('role', treeNode.id)
        alert(treeNode.id)

        //pospDataTable.clearPipeline().draw();
    }

    function getFontCss(treeId, treeNode) {
        return (!!treeNode.highlight) ? {color: "#A60000"} : {color: "#333"};
    }

    //var nodeList
    var nodeList = []
    // 搜索功能实现
    function tree_search(id, key, value) {
        var treeObj = $.fn.zTree.getZTreeObj("treeDemo");
        var allNodes = treeObj.transformToArray(treeObj.getNodes());
        if (value == "") {
            treeObj.expandAll(true);
            updateNodes(false, allNodes)
            return;
        }
        var nodes = treeObj.getNodesByParamFuzzy("name", value);
        for (var i = 0; i < allNodes.length; i++) {
            allNodes[i].highlight = false;
            treeObj.updateNode(allNodes[i]);
        }
        treeObj.expandAll(false);
        treeObj.expandNode(treeObj.getNodes()[0], true);
        for (var i = 0; i < nodes.length; i++) {
            nodes[i].highlight = true;
            // 更新节点，让高亮生效
            treeObj.updateNode(nodes[i]);
            treeObj.expandNode(nodes[i].getParentNode(), true);
        }
    }

    function updateNodes(highlight, nodeList) {
        var zTree = $.fn.zTree.getZTreeObj("treeDemo");
        for (var i = 0, l = nodeList.length; i < l; i++) {
            nodeList[i].highlight = highlight;
            zTree.updateNode(nodeList[i]);
        }
    }
})


