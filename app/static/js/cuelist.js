// cuelist.js
// Javascript Funktionen für Cuelisten:

function activateCuelistbuttons () {
  // Go Button:
  $(".gobutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    $.get ("/cuelist/go", args);
  });

  // Pause Button:
  $(".pausebutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    $.get ("/cuelist/pause", args);
  });

  // Minus Button:
  $(".minusbutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    $.get ("/cuelist/minus", args);
  });
  
  // Plus Button:
  $(".plusbutton").click ( function (){
    var index = $(this).attr ("index");
    var args = {index:index};
    $.get ("/cuelist/plus", args);
  });
  
}

function cuelistStatus (num, data) {
  // Statusdaten in macro cl_status anzeigen:
  var numstring = num.toString ();
  
  // ID und Text
  $("#currentid-"+numstring).text (data["currentline"]["Id"]);
  $("#nextid-"+numstring).text (data["nextline"]["Id"]);
  $("#currenttext-"+numstring).text (data["currentline"]["Text"]);
  $("#nexttext-"+numstring).text (data["nextline"]["Text"]);

  $("#fadein-indicator-"+numstring)
    .attr ("aria-valuenow", data["fading_in"])
    .css ("width", data["fading_in"] + "%");
  $("#fadeout-indicator-"+numstring)
    .attr ("aria-valuenow", data["fading_out"])
    .css ("width", data["fading_out"] + "%");

  // Pause-Status:
  var pauseid = ".pausebut-" + numstring;
  if (data["is_paused"] == "true") {
    $(pauseid).removeClass ("btn-secondary").addClass ("btn-warning");
  } else {
    $(pauseid).removeClass ("btn-warning").addClass ("btn-secondary");
  };
}

function periodic_allcueliststatus () {
  // siehe: https://stackoverflow.com/questions/5052543/how-to-fire-ajax-request-periodically
  // aktuelle Faderwerte der Cuelist Levels am Schieberegler zeigen:    
  // verwendet in cl-pages.html   
  $.ajax ({
    url: "/cuelist/allstatus", 
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
      var data;
      for (i = 0; i < clstatus.length; i++){
        data = clstatus[i] ;
        cuelistStatus (i, data);
      };

    },
    complete: function () {
      setTimeout (periodic_allcueliststatus, 500);
    }
  }); // ende $.ajax
}
  

// ----------------------------------------------------------------------------
// Filebutton 'ansehen'
// verwendet in Tabellen und Sliderzeilen, die Cuelisten enthalten:
// cl-pages, cl-pages-setup
// siehe auch: activateCuedetails ()

function activateCuelistDetails () {
  // Button "Editor"  
  $("button.cuelistview").on ("click", function ()  {

    var filename = $(this).attr ("name");
    var index = $(this).attr ("index");
    let url = "/cuelist/editor?filename=" + filename + "&index=" + index;
    location.href = url;
    return false;
  }); // ende $ cuelistview

};

  
  