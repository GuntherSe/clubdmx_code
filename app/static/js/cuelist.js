// cuelist.js
// Javascript Funktionen für Cuelisten:

function activateCuelistbuttons () {
  // Go Button:
  $(".gobutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    $.get ("/cuelist/go", args);
    // var pauseid = ".pausebut-" + index;
    // $.get ("/cuelist/go", args, function () {
    //   $(pauseid).removeClass ("btn-warning").addClass ("btn-secondary");
    // });
  });

  // Pause Button:
  $(".pausebutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    $.get ("/cuelist/pause", args);
    // var pauseid = ".pausebut-" + index;
    // $.get ("/cuelist/pause", args, function () {
    //   $(pauseid).removeClass ("btn-secondary").addClass ("btn-warning");
    // });
  });

  // Minus Button:
  $(".minusbutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    // var pauseid = ".pausebut-" + index;
    $.get ("/cuelist/minus", args);
  });
  
  // Plus Button:
  $(".plusbutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    // var pauseid = ".pausebut-" + index;
    $.get ("/cuelist/plus", args);
  });
  
}

function cuelistStatus (num, data) {
  // Statusdaten in macro cl_status anzeigen:
  var numstring = num.toString ();
  var val = data[num] ;
  // ID und Text
  $("#currentid-"+numstring).text (val["currentid"]);
  $("#nextid-"+numstring).text (val["nextline"]["Id"]);
  $("#currenttext-"+numstring).text (val["currentline"]["Text"]);
  $("#nexttext-"+numstring).text (val["nextline"]["Text"]);

  $("#fadein-indicator-"+numstring)
    .attr ("aria-valuenow", val["fading_in"])
    .css ("width", val["fading_in"] + "%");
  $("#fadeout-indicator-"+numstring)
    .attr ("aria-valuenow", val["fading_out"])
    .css ("width", val["fading_out"] + "%");

  // Pause-Status:
  var pauseid = ".pausebut-" + numstring;
  if (val["is_paused"] == "true") {
    $(pauseid).removeClass ("btn-secondary").addClass ("btn-warning");
  } else {
    $(pauseid).removeClass ("btn-warning").addClass ("btn-secondary");
  };
}

function periodic_cueliststatus () {
// siehe: https://stackoverflow.com/questions/5052543/how-to-fire-ajax-request-periodically
// aktuelle Faderwerte der Cuelist Levels am Schieberegler zeigen:       
// var sliderlevels;
$.ajax ({
    url: "/cuelist/status", 
    success: function(data) {
      var jdata = $.parseJSON(data);
      // Slider:
      var sliderlevels = jdata["levels"];
      var i;
      for (i = 0; i < sliderlevels.length; i++){
          faderStatus (i, sliderlevels);
      };
      // Status:
      var clstatus = jdata["status"];
      for (i = 0; i < clstatus.length; i++){
        cuelistStatus (i, clstatus);
      };

    },
    complete: function () {
      setTimeout (periodic_cueliststatus, 200);
    }
}); // ende $.ajax
}

  
  