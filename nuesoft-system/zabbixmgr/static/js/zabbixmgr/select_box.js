/**
 * Created by Administrator on 2017/12/14.
 */

function changeF(this_) {
    $("#makeupCo").val($(this_).find("option:selected").text());
    $("#typenum").css({"display":"none"});
}

 function changeF_1(this_) {
    $("#makeupCo_1").val($(this_).find("option:selected").text());
    $("#typenum_1").css({"display":"none"});
}

function setfocus(this_){
    $("#typenum_1").css({"display":"none"});
    $("#typenum").css({"display":""});
    var select_1 = $("#typenum");
    select_1.html('')
    if ($("#makeupCo").val().length == 0) {

        $.each(arrData,function(pF,pS){
            var option = $("<option></option>").text(pF);
            select_1.append(option);
        })
    } else {
        $.each(arrData,function(pF,pS){
            if(pF.substring(0,this_.value.length).indexOf(this_.value)==0){
                var option = $("<option></option>").text(pF);
                select_1.append(option);
            }
        });
    }

}

 function setfocus_1(this_){
     $("#typenum").css({"display":"none"});
     $("#typenum_1").css({"display":""});
     var select_1 = $("#typenum_1");
     select_1.html('');
     var flag = 0;

     $.each(arrData, function(pF, pS) {
         if ($("#makeupCo").val() == pF) {
             flag = 1
             $.each(arrData[pF],function(pV, pS){
                if(pS.substring(0,this_.value.length).indexOf(this_.value)==0){
                    var option = $("<option></option>").text(pS);
                    select_1.append(option);
                }
             });
         }
     });

     if ($("#makeupCo_1").val().length == 0 && flag == 0) {
         $("#typenum_1").css({"display":"none"});
     }
}

function setinput(this_){
    stl_value = '';
    var select = $("#typenum");
    select.html("");
    $.each(arrData,function(pF,pS){
        if(pF.substring(0,this_.value.length).indexOf(this_.value)==0){
            var option = $("<option></option>").text(pF);
            select.append(option);
        }
    });
    if ($('#makeupCo').val().length == 0) {
        $("#typenum").css({"display":""});
    }
}

function setinput_1(this_){
    var input_val = $("#makeupCo").val();
    var select_val = $("#typenum").val();
    var select = $("#typenum_1");
    select.html("");
    $.each(arrData, function(pF, pS){
       if (input_val == pF) {
           $.each(arrData[pF],function(pV, pS){
            if(pS.substring(0,this_.value.length).indexOf(this_.value)==0){
                var option = $("<option></option>").text(pS);
                select.append(option);
            }
        });
       }
    });
    if ($("#makeupCo_1").val().length == 0) {
        $("#typenum_1").css({"display":""});
    }
}
