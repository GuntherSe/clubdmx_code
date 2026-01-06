/* Clubdmx.js: JS Sammlung für Projekt CLUBDMX */


/* int to string with leading zeros
siehe: https://stackoverflow.com/questions/2998784/how-to-output-integers-with-leading-zeros-in-javascript?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
*/

function int_to_str(num, size) {
  var s = num+"";
  while (s.length < size) s = "0" + s;
  return s;
}
/* integer aus String auslesen: 
https://stackoverflow.com/questions/10003683/how-can-i-extract-a-number-from-a-string-in-javascript
*/
function extract_int (str)  {
  var num = str.replace(/[^0-9\.]/g,'');
  return Math.round (num);
  // var part = str.match(/([A-Za-z\-_]+)([0-9]+)/);
  // return part[2];
};

// ---------------------------------------------------------------------------
// Toggle Fullscreen:
// https://developers.google.com/web/fundamentals/native-hardware/fullscreen


// --- History Back -------------------------
// Funktion zum Bau eines Back-Buttons:
function historyBack() {
  event.preventDefault ();
  var history = $("#sessiondata").attr ("history");
  if (history) {
    window.location.href = history;
  } else {
    window.history.back();
  }
  return false;
}

// --- Message -----------------------------------------------------------------
// nicht in Verwendung
function jsmessage (data)  {
  var message = "<p class='alert-danger'>" + data + "</p>";
  $("#jsmessage").html (message).delay(2500)
  .fadeOut(1600, function () {
    $(this).empty().show();
  });

}
// --- Topcue Navigation anzeigen/verbergen ---------------------------------
function resizeStage () {
  // wird in stage.js neu definiert
  // console.log ("Resize:nothing to do");
}

function showSecondNav () {
  $("#secondNav").show ();
  var navheight = $("#primaryNav").height () + $("#secondNav").height ();
  $("#menu").css ("padding-top", navheight);
  resizeStage ();
}

function hideSecondNav () {
  $("#secondNav").hide ();
  var navheight = $("#primaryNav").height ();
  $("#menu").css ("padding-top", navheight);
  resizeStage ();
}


// ---------------------------------------------------------------------
// Slider in cuefader und executer:
function activateSlider (num, sliderlevel, fadertype) {
  var numstring = num.toString();
  // var cmdstring;
  // if (fadertype == "cuefader") {
  //   // cuefader
  //   cmdstring = "/sliderlevel/" + numstring;
  // } else {
  //   // cuelist level fader
  //   cmdstring = "/cuelistlevel/" + numstring;
  // }
  $("#"+ fadertype + "-" + +numstring)
    .val(sliderlevel[num]);
}

// ----------------------------------------------------------------------------
// Buttons in cuebuttons und executer:
function activateCuebuttons () {
  $(".cuebutton").click ( function (event){
    socket.emit ("cuebutton pressed", {
      id: $(this).attr ("id"),
      index: $(this).attr("index")
    });
    return false;
  });
}

// ----------------------------------------------------------------------------
// Filebuttons 'ansehen' und '>Topcue' 
// verwendet in Tabellen und Sliderzeilen, die Cues enthalten

function activateCuedetails () {
  // Button "ansehen"  in Cueinfo und cuefader
  $("button.cueview").on ("click", function ()  {

    var filename = $(this).attr ("name");
    let url = "/cue/cuepage?filename=" + filename 
              + "&history=" + window.location.href;
    location.href = url;
    return false;

  }); // ende $ cueview

  // --- Cue in Topcue editieren :
  $("button.cueedit").on ("click", function () {
    event.stopPropagation();
    var filename = $(this).attr ("name")
    var args = {filename:filename};
    
    showSecondNav ();

    $.get ("/cue/cueedit", args, function (data) {
      var jdata = JSON.parse (data);
      if (jdata != "false") {
        $("#showCueModal").trigger ("click");
        $("#dialogModal").on ("shown.bs.modal", function () {
          $(".selectDiv").html (filename);
          $("#faderspace").html (jdata["table"]);
          saveEditButton (filename);
          var heads   = jdata["heads"];
          var attribs = jdata["attribs"];
          var levels  = jdata["levels"];
          // console.log ("Levels: " +JSON.stringify (levels));
          for (var i=0; i < heads.length; i++){
              activateAttribSlider (heads[i], attribs[i], levels[i],
                                  '/cue/cueedit' );
          };
        }); // on shown
      }; // if
    }); // get
  });
};

function saveEditButton (filename) {
  // Save-Button für Cue-Edit:
  $("#saveCueButton").on ("click", function () {
    var args = {filename:filename};
    $.get ("/cuechild/update_cue", args, function(){
      location.reload ();
    });
  });
};


function activateAttribSlider (head, attrib, level, url) {
  // Slider fürs Cue-Edit erzeugen
  // siehe: cuefader.html, stage.html
  $('#attrib-'+head+attrib)
    .val (level)
    .on ("input", function () {
      var args = {head:head, attrib:attrib, level:this.value};
      $.post (url, args);
      $("#sessiondata").attr ("topcuecontent", "true");
    });
};
      

function modaldialogToPython (clickid, url, args) {
// bei Klick auf clickId wird url aufgerufen:
// Modaldaten werden geholt
// mit Drücken des selectButton werden die Daten
// an den Server gepostet, anschließend: location.reload
  $(clickid).on ("click", function () {
    $.get (url, args, function (data) {
      $("#dialogModal").html (data);
      $("#viewModal").modal ();
      // auswerten bei Strings:
      $("#selectButton").on ('click', function(){
          var newname = $("#input-text").first().val();
          var data = {selectButton:"true", name:newname};
          // neu 6.2.2021:
          data.args = JSON.stringify (args);
          $.post (url, data, function () {
              location.reload (); 
          });
      });
      $(document).keypress (function (e) {
        if (e.keycode == 13 || e.which == 13) {
          var newname = $("#input-text").first().val();
          var data = {selectButton:"true", name:newname};
          // neu 6.2.2021:
          data.args = JSON.stringify (args);
          $.post (url, data, function () {
              location.reload (); 
          });
        };
      });
      $(".close-modal").on ("click", function(){
          //console.log ("Modal close");
          $.post ("/forms/modalclose");
      });
    });
  });
};

function checkModal (clickid) {
  // Modal neu anzeigen, wenn die Validierung des Form nicht gültig war
  // bei SelectField nicht nötig, bei anderen Feldern schon
  var active;
  active = $("#sessiondata").attr ("modalactive");
  if (active == "true") {
      $(clickid).trigger ("click");
  };
};

function csvSavediscardButtons () {
//  if ($("#sessiondata").attr ("csvchanges") == "true") {
  if ($("#csvtable").attr ("changes") == "true") {
      $(".csvchanges").removeClass ("d-none"); 
  } else {
    $(".csvchanges").addClass ("d-none"); 
  };
};

// siehe: https://stackoverflow.com/questions/5052543/how-to-fire-ajax-request-periodically
// function periodic_commonstatus () {
//   // periodischer Aufruf zum Holen der variablen Basisdaten
//     $.ajax ({
//         url: "/getinfo/commonstatus", 
//         success: function(data){
//           var jdata = JSON.parse (data);
//           //console.log ("common: " + JSON.stringify (jdata));
//           // if (jdata["editmode"] == "select") {
//           //   setEditmode ("select");
//           // } else {
//           //   setEditmode ("edit");
//           // };
//           // Buttons zu CSV-Zeilen cut/paste:
//           // werden von der aktuellen Seite verwaltet, d.h. wenn Zeilen 
//           // ausgewählt werden, dann sind diese sichtbar.
//           // insert/clear sind per User auf allen betreffenden Seiten
//           // sichtbar (wenn Daten im Clipboard sind)
//           if (jdata["csvclipboard"] == "true") {
//             $(".csvClipboard").removeClass ("d-none");
//           } else {
//             $("csvClipboard").addClass ("d-none");
//           };
//           // initMouseMode ();
//           // Topcue Menü anzeigen:
//           // if (jdata["topcuecontent"] == "true") {
//           //   showSecondNav ();
//           // } else {
//           //   hideSecondNav ();
//           // }; 

//         },
//         complete: function () {
//         setTimeout (periodic_commonstatus, 1000);
//         }
//     }); // ende $.ajax
//   }

// ----- Socket -------------------------------------------------------------
// siehe socketio_basic:
var ip = location.host;
// alert ("IP des Host: " + ip);
var socket = io.connect(ip);

socket.on('after connect', function(msg) {
    console.log('After connect', msg);
});

socket.on('update slidervalue', function(msg) {
    //console.log('slider value updated');
    let elem = $('#' + msg.who);
    if (elem.is (":focus") ) {} else {
      elem.val(msg.data);}
});

socket.on ("init slider position", function(msg) {
  let fadertype = msg.fadertype;
  var idstring;
  if (fadertype == "cuefader") {
    idstring = "#cuefader-";
  } else {
    idstring = "#cuelistfader-";
  };
  // console.log ("init slider: " + msg.data + " " + msg.data.length);
  for ( var fader=0; fader < msg.data.length; fader++ ) {
    $(idstring + fader.toString()).val (msg.data[fader]);
  };

});

socket.on('update buttonstatus', function(msg) {
    // console.log('button status updated');
    let but_id = "but-"+msg.index;
    let status = msg.status;
    var parentcard = $("#"+but_id).parent (".card");
    if ( status == 0 ) {
      parentcard.removeClass ("active");
    } else {
      parentcard.addClass ("active");
    };
});

socket.on ("update clipboard status", function (msg) {
  if (msg.status == "true") {
    $(".csvClipboard").removeClass ("d-none");
  } else {
    $("csvClipboard").addClass ("d-none");
  };
});


socket.on ("update topcue status", function (msg) {
  if (msg.status == "true") {
    showSecondNav ();
  } else {
    hideSecondNav ();
  }; 
});


// --- Navigation für Topcue und CSV-Buttons: --------------------------------

$(document).ready (function() {

  let session = $("#sessiondata");
  // Topcue:
  if (session.attr ("topcuecontent") == "true") {
    showSecondNav ();
  } else {
    hideSecondNav ();
  }; 
  // Clipboard:
  if (session.attr ("csvclipboard") == "true") {
    $(".csvClipboard").removeClass ("d-none");
  } else {
    $("csvClipboard").addClass ("d-none");
  };
  // editmode:
  if (session.attr ("editmode") == "select") {
    setEditmode ("select");
  } else if (session.attr ("editmode") == "edit"){
    setEditmode ("edit");
  };

  // periodic_commonstatus ();
  // Mousemode Optionen:
  initMouseMode ();

  $(document).on ("keydown", function (event) {
    if (event.which == 113) { // F2
      toggleMousemode ();
    };
  })
  enableChangeMousemode (".mousemode-edit", "edit");
  enableChangeMousemode (".mousemode-select", "select");

  $(".selectDiv").empty();
  modaldialogToPython ("#showCueModal", "/cuechild/cuemodal");
  modaldialogToPython (".topview", "/cuechild/topview");
  filedialogToPython  (".topsavecue", "/cuechild/topsave/cue");
  modaldialogToPython  (".topsavefader", "/cuechild/topsave/fader");
  modaldialogToPython  (".topsavebutton", "/cuechild/topsave/button");
  modaldialogToPython  (".topsavecuelist", "/cuechild/topsave/cuelist");
});