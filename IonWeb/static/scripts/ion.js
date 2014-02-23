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