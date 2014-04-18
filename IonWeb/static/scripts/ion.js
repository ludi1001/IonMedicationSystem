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
  
  $(window).resize(function() {
    if($("#menu-icon").is(":visible")) {
      $("#main-menu").hide();
    }
    else {
      $("#main-menu").show();
    }
    $("#content-container").fadeTo("fast",1);
  });
  
  setupAjax();
  
  notification.initialize();
  
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
  
  function refreshView() {
    
  }
  
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
      var x = a.creation_date; //sort by creation date because reading the notification results in a change in last_modified
      var y = b.creation_date;
      return (x > y ? -1 : (x < y ? 1 : 0));
    });
    
  }
  
  function cleanNotifications(list) {
    //performs any pre-processing on the received list before appending to notification list
    list.forEach(function(n) {
      n.last_modified = new Date(n.last_modified);
      n.creation_date = new Date(n.creation_date);
    });
    return list;
  }
  
  my.initialize = function() {
    //request all notifications
    var today = new Date();
    today.setHours(0);
    today.setMinutes(0);
    today.setSeconds(0);
    today.setMilliseconds(0);
    var request = {"earliest":serializeTime(today),"latest":serializeTime(new Date())};
    this.fetch(request);
  }
  my.fetch = function(request) {
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
    
    this.refreshView();
  }  
  my.serialize = serializeTime;
  my.refreshView = function() {
    $("#notifications").empty();
    var unread = false;
    var count = 0;
    for(var i = 0; i < notification_list.length; ++i, ++count) {
      if(count > 10) break;
      var n = notification_list[i];  
      var html = [];
      html.push("<li>");
      html.push("<time>");
      html.push(n.creation_date.toLocaleDateString() + " " + n.creation_date.toLocaleTimeString());
      html.push("</time>");
      html.push("Test");
      html.push("<a>Dismiss</a>");
      html.push("</li>");
      var li = $(html.join(" "));
      if(n.unread)
        li.addClass("unread");
      $("#notifications").append(li);
      
      unread |= n.unread;
    }
    if(unread) {
      $("#notification-icon").attr("src", "/static/images/mail2.png");
    }
    else {
      $("#notification-icon").attr("src", "/static/images/mail1.png");
    }
  }
  my.printNotifications = function() {
    console.log(notification_list);
  }
  return my;
})();