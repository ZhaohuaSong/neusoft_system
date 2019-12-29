//获取基本信息做统计显示
jQuery(function ($) {

    //获取服务器地址
    var host_url = encodeURI(window.location.host);

    
    //初始化报文管理统计信息
    init_packmanage(host_url);


    //定义实现初始化报文管理统计信息逻辑
    function init_packmanage(host_url){
        /*******************
        packmanage_url:外面传入进来
        *******************/

        var url = 'http://' + host_url + '/packmanage/reomte/protocoltype/list?option=get_protocol_number';    
        $.get( url, function(data, status){
                     
                    if(data["code"]=="00"){
                        jQuery("#lb_remote_protocol_number").text(data["remote_protocol_number"])
                    }
                    else{
                    }
                })
        
    }
})