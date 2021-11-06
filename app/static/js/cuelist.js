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
}

function periodic_cueliststatus () {
// siehe: https://stackoverflow.com/questions/5052543/how-to-fire-ajax-request-periodically
// aktuelle Faderwerte der Cuelist Levels am Schieberegler zeigen:       
var sliderlevels;
$.ajax ({
    url: "/getinfo/cl_sliderval", 
    success: function(data){
    sliderlevels = $.parseJSON(data);
    var i;
    for (i = 0; i < sliderlevels.length; i++){
        faderStatus (i, sliderlevels);
        // $(".slider").width (sliderwidth);
    };
    },
    complete: function () {
    setTimeout (periodic_cueliststatus, 1000);
    }
}); // ende $.ajax
}

  
  