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
  
  function serializeTime(time) {
    
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
  }
  
  my.initialize = function() {
    //request all notifications
    request = 
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