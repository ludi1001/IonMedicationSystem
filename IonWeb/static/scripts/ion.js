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
  setupAjax();
  if($("#menu-icon").length > 0) {
    $("#menu-icon").click(function() {
      if($("#main-menu").is(":hidden")) {
        $("#content-container").fadeTo("fast",.2);
      }
      else {
        $("#content-container").fadeTo("fast",1);
      }
      //hide notifications if it is open
      if(!$("#main-menu").is(":visible"))
        $("#notifications").hide();
      
      $("#main-menu").slideToggle("fast");
    });
  }
  if($("#notification-icon").length > 0) {
    $("#notification-icon").click(function() {
      $(this).attr("src","/static/images/mail.png");
      notification.markNewlyRead();
      //hide main menu if necessary
      if(!$("#notifications").is(":visible") && $("#menu-icon").is(":visible"))
        $("#main-menu").hide();

      //gray out background content
      if($("#notifications").is(":hidden")) {
        $("#content-container").fadeTo("fast",.2);
      }
      else {
        $("#content-container").fadeTo("fast",1);
      }
      
      $("#notifications").slideToggle("fast");
      
    });
    notification.initialize();
  }
  
  $(window).resize(function() {
    if($("#menu-icon").is(":visible")) {
      $("#main-menu").hide();
    }
    else {
      $("#main-menu").show();
    }
    $("#content-container").fadeTo("fast",1);
    $("#notifications").hide();
  });

  
});

//notification manager
var notification = (function() {
  var URL_REQUEST = "/notification/get";
  var URL_READ = "/notification/read";
  var IDEAL_NUM_NOTIFICATIONS = 10;
  var REFRESH_TIME = 5000;
  var REFRESH_TIME_UPDATE = 5000;
  
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
  
  var newlyUnread = false; //did we receive any new notifications
  var firstCall = true; //on first call to append notifications, ignore new notifications
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
        if(!firstCall)
          newlyUnread = true;
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
    //periodically check for updates
    setInterval(function() {
      var time = new Date(0); //Jan 1, 1970
      if(notification_list.length > 0) {
        time = notification_list[0].creation_date; //we assume the list is sorted
        time = new Date(time.getTime() - 1000); //push time back a little earlier just in case that there's a new notification at exactly the same time
      }
      my.fetch({'earliest':serializeTime(time)});
    }, REFRESH_TIME);
    
    var lastUpdateTime = new Date();
    setInterval(function() {
      my.fetch({"updated_since":serializeTime(lastUpdateTime)});
      lastUpdateTime = new Date();
    }, REFRESH_TIME_UPDATE);
    
    //request notifications day by day until we have at least 10 notifications
    my.fetch({"recent":IDEAL_NUM_NOTIFICATIONS});
  }
  my.fetchNextNotifications = function(n) { //fetches (approximately) next n notifications following the last notification
    var time = new Date();
    if(notification_list.length > 0) {
      time = notification_list[notification_list.length - 1].creation_date;
      time = new Date(time.getTime() + 1000); //this is why it is approximate
    }
    my.fetch({"latest":serializeTime(time),"recent":n});
  }
  my.fetch = function(request) {
    //console.log(request);
    $.ajax({
      url:URL_REQUEST,
      type: 'POST',
      data: JSON.stringify(request),
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      async: false
    }).done(function(data) {
      my.insertNotifications(data);
    });
    
    this.refreshView();
  }
  my.insertNotifications = function(data) {
    appendNotifications(cleanNotifications(data));
  }
  my.serialize = serializeTime;
  my.markRead = function(id, callback) { //mark notification with id as read
    var request = {"id":id};
    console.log(request);
    $.ajax({
      url:URL_READ,
      type: 'POST',
      data: JSON.stringify(request),
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      async: false
    }).done(function(data) {
      if(callback) callback(data);
    });
  }
  my.refreshView = function() {
    
    $("#notifications").empty();
    var li = $("<li class='all-notifications'><div><a href='/notification/'>See all notifications</a></div></li>");
    $("#notifications").append(li);
    
    var unread = false;
    var count = 0;
    for(var i = 0; i < notification_list.length; ++i, ++count) {
      if(count > IDEAL_NUM_NOTIFICATIONS) break;
      var n = notification_list[i];  
      var html = [];
      html.push("<li>");
      html.push("<div class='header'>");
      html.push("<time>");
      html.push(n.creation_date.toLocaleDateString() + " " + n.creation_date.toLocaleTimeString());
      html.push("</time>");
      html.push("</div>");
      html.push(n.message);
      html.push("</li>");
      var li = $(html.join(""));
      if(n.unread) {
        li.addClass("unread");
        li.data("index",i);
      }
      $("#notifications").append(li);
      
      unread |= n.unread;
    }
    $("#notifications li.unread div.header").append('<a class="dismiss">Dismiss</a>');
    $("#notifications li div.header a.dismiss").click(function() {
      var li = $(this).parent().parent();
      //mark as read
      my.markRead(notification_list[li.data("index")].id, function(data) {
        //get read of unread and dismiss button
        li.removeClass("unread");
        li.children("div.header").children("a.dismiss").remove();
        notification_list[li.data("index")].unread = false; //assume it went through, we'll get an updated copy later
      });
    });
    if(firstCall)
      newlyUnread = unread;
    if(newlyUnread) {
      $("#notification-icon").attr("src", "/static/images/mail2.png");
    }
    else {
      $("#notification-icon").attr("src", "/static/images/mail.png");
    }
    firstCall = false;
  }
  my.markNewlyRead = function() {
    newlyUnread = false;
  }
  my.getNotifications = function() {
    return notification_list;
  }
  my.printNotifications = function() {
    console.log(notification_list);
  }
  return my;
})();