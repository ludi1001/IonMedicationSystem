function setupAjax() {
  //setup ajax
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');
  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  $.ajaxSetup({
      crossDomain: false, // obviates need for sameOrigin test
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type)) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
}


$(document).ready(function() {
  $("#menu-icon").click(function() {
    if($("#main-menu").is(":hidden")) {
      $("#content-container").fadeTo("fast",.2);
    }
    else {
      $("#content-container").fadeTo("fast",1);
    }
    $("#main-menu").slideToggle("fast");
  });
  $("#notification-icon").click(function() {
    $("#notifications").slideToggle("fast");
  });
  
  setupAjax();
});
$(window).resize(function() {
  if($("#menu-icon").is(":visible")) {
    $("#main-menu").hide();
  }
  else {
    $("#main-menu").show();
  }
  $("#content-container").fadeTo("fast",1);
});

//notification manager
var notification = (function() {
  var URL = "/notification/get";
  var my = {};
  var notification_list = [];
  
  function serializeTime(date) {
   var d = date.getDate();
   var m = date.getMonth() + 1;
   var y = date.getFullYear();
   var H = date.getHours();
   var M = date.getMinutes();
   var S = date.getSeconds();
   return '' + (m<=9 ? '0' + m : m) + '/' + (d <= 9 ? '0' + d : d) + '/' + y + ' ' + 
      (H <= 9 ? '0' + H : H) + ':' + (M <= 9 ? '0' + M : M) + ':' + (S <= 9 ? '0' + S : S);
   }  
   
  my.serialize = serializeTime;
  
  function appendNotifications(list) {
    for(var i = 0; i < list.length; ++i) {
      //this is very inefficient but w/e
      var j;
      for(j = 0; j < notification_list.length; ++j) {
        if(notification_list[j].id == list[i].id)
          break;
      }
      if(j == notification_list.length) {
        //notification does not exist
        notification_list.push(list[i]);
      }
      else {
        //replace old notification just in case
        notification_list[j] = list[i];
      }
    }
    //resort list by time
    notification_list.sort(function(a,b) {
      var x = a.last_modified;
      var y = b.last_modified;
      return (x > y ? -1 : (x < y ? 1 : 0));
    });
  }
  
  function cleanNotifications(list) {
    //performs any pre-processing on the received list before appending to notification list
    list.forEach(function(n) {
      n.last_modified = new Date(n.last_modified);
    });
    return list;
  }
  
  my.initialize = function() {
    //request all notifications
    var request = {"earliest":serializeTime(new Date(2013,1,1)),"latest":serializeTime(new Date())};
    $.ajax({
      url:URL,
      type: 'POST',
      data: JSON.stringify(request),
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      async: false
    }).done(function(data) {
      appendNotifications(cleanNotifications(data));
    });
  }
  my.printNotifications = function() {
    console.log(notification_list);
  }
  return my;
})();