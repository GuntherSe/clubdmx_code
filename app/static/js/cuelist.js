// cuelist.js
// Javascript Funktionen für Cuelisten:

function activateCuelistbuttons () {
  // Go Button:
  $(".gobutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    var pauseid = "#cuelistpause-" + index;
    $.get ("/cuelist/go", args, function () {
      $(pauseid).removeClass ("btn-warning").addClass ("btn-secondary");
    });
  });

  // Pause Button:
  $(".pausebutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    var pauseid = "#cuelistpause-" + index;
    $.get ("/cuelist/pause", args, function () {
      $(pauseid).removeClass ("btn-secondary").addClass ("btn-warning");
    });
  });
}

function cuelistStatus (num, data) {
  // Statusdaten in macro cl_status anzeigen:
  var numstring = num.toString ();
  var val = data[num] ;
  // var strval;
  $("#currentid-"+numstring).text (val["currentid"]);
  $("#nextid-"+numstring).text (val["nextid"]);
  // TODO: Fade-Status
  // strval = val["fading_in"];
  $("#fadein-indicator-"+numstring)
    .attr ("aria-valuenow", val["fading_in"])
    .css ("width", val["fading_in"] + "%");
  $("#fadeout-indicator-"+numstring)
    .attr ("aria-valuenow", val["fading_out"])
    .css ("width", val["fading_out"] + "%");
}

function periodic_cueliststatus () {
// siehe: https://stackoverflow.com/questions/5052543/how-to-fire-ajax-request-periodically
// aktuelle Faderwerte der Cuelist Levels am Schieberegler zeigen:       
// var sliderlevels;
$.ajax ({
    url: "/getinfo/cl_status", 
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

  
  