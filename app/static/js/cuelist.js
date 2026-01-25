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
  // nicht verwendet: socketio übermittelt aktuellen Status
  // siehe: https://stackoverflow.com/questions/5052543/how-to-fire-ajax-request-periodically
  // aktuelle Faderwerte der Cuelist Levels am Schieberegler zeigen:    
  // verwendet in cl-pages.html   
  $.ajax ({
    url: "/cuelist/allstatus", 
    success: function(data) {
      var jdata = $.parseJSON(data);
      // Status:
      var clstatus = jdata["status"];
      var data;
      for (i = 0; i < clstatus.length; i++){
        data = clstatus[i] ;
        cuelistStatus (i, data);
      };
      // Slider:
      // var sliderlevels = jdata["levels"];
      // var i;
      // try {
      //   for (i = 0; i < sliderlevels.length; i++){
      //       faderStatus (i, sliderlevels);
      //   };
      // }
      // catch(err) {
      //   console.log ("Fehler in Sliderlevel: " + err);
      // }
    },
    complete: function () {
      setTimeout (periodic_allcueliststatus, 500);
    }
  }); // ende $.ajax
}
  
// An event handler for a change of value 
$('input.inputslider').on('input', function(event) {
    socket.emit('slider value changed', {
        who: $(this).attr('id'),
        fadertype: "cuelistfader",
        data: $(this).val()
    });
    return false;
});

socket.on ("update cueview", function (data){
  // console.log (data)
  var numstring = data["listnum"];
  var clIndex = $("#cuelistindex").attr ("index");
  $("#currentid-"+numstring).text (data["current_id"]);
  $("#nextid-"+numstring).text (data["next_id"]);
  $("#currenttext-"+numstring).text (data["current_text"]);
  $("#nexttext-"+numstring).text (data["next_text"]);

  $("#fadein-indicator-"+numstring)
    .attr ("aria-valuenow", data["fading_in"])
    .css ("width", data["fading_in"] + "%");
  $("#fadeout-indicator-"+numstring)
    .attr ("aria-valuenow", data["fading_out"])
    .css ("width", data["fading_out"] + "%");

  if (numstring == clIndex) { // Tabellenzeilen Hintergrundfarbe:
    let currentid = "tr.id-" + data["current_id"].replace ('.', '-');
    let nextid = "tr.id-" + data["next_id"].replace ('.', '-');
    $("tr").removeClass ("table-info table-success")
    $(currentid).addClass ("table-info");
    $(nextid).addClass ("table-success");
  }

  // Pause-Status:
  var pauseid = ".pausebut-" + numstring;
  if (data["is_paused"] == "true") {
    $(pauseid).removeClass ("btn-secondary").addClass ("btn-warning");
  } else {
    $(pauseid).removeClass ("btn-warning").addClass ("btn-secondary");
  };

});

// socket.on('update slidervalue', function(msg) {
//     //console.log('slider value updated');
//     let elem = $('#' + msg.who);
//     if (elem.is (":focus") ) {} else {
//       elem.val(msg.data);}
// });


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

  
  