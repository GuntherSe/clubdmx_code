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
// Funktion zum Slider erzeugen:
function makeSlider (num, sliderlevel, fadertype) {
  var numstring = num.toString();
  var cmdstring;
  if (fadertype == "cuefader") {
    // cuefader
    cmdstring = "/sliderlevel/" + numstring;
  } else {
    // cuelist level fader
    cmdstring = "/cuelistlevel/" + numstring;
  }
  $("#sl-"+numstring)
    .slider({value:sliderlevel[num],
              max:255,
              slide: function (event, ui){
                  var sliderval = {level:ui.value};
                  $.post (cmdstring, sliderval);
              }
    });
}

function faderStatus (num, statusarray) {
  // level aus der fadertable wird auf Fader übertragen
  var numstring = num.toString ();
  var level = statusarray[num] ;
  $("#sl-"+numstring).slider ("option", "value", level);
}

function periodic_faderstatus () {
  // siehe: https://stackoverflow.com/questions/5052543/how-to-fire-ajax-request-periodically
  // aktuelle Faderwerte der Cuefader am Schieberegler zeigen:       
  var sliderlevels;
  // var sliderwidth = $(".col-8").width();
  $.ajax ({
    url: "/getinfo/sliderval", 
    success: function(data){
      sliderlevels = $.parseJSON(data);
      var i;
      for (i = 0; i < sliderlevels.length; i++){
          faderStatus (i, sliderlevels);
          // $(".slider").width (sliderwidth);
      };
    },
    complete: function () {
      setTimeout (periodic_faderstatus, 1000);
    }
  }); // ende $.ajax
}


// ----------------------------------------------------------------------------
// Buttons in cuebuttons und executer:

function activateCuebuttons () {
  $(".cuebutton").click ( function (){
    var status;
    var parentcard = $(this).parent (".card");
    if ( parentcard.hasClass ("active") ) {
      parentcard.removeClass ("active");
    } else {
      parentcard.addClass ("active");
    };
    var index = $(this).attr ("index");
    //console.log ("Button: " + index);
    var args = {index:index};
    $.get ("/buttonpress", args);
  });
}

function buttonStatus (num, statusarray) {
// Anzeige, ob Button aktiv oder nicht aktiv ist.
  var numstring = (num).toString();
  var parentcard = $('#but-'+numstring).parent (".card");
  if (statusarray[num] == 1) {
      parentcard.addClass ("active");
  } else {
      parentcard.removeClass ("active");
  }
};

// siehe: https://stackoverflow.com/questions/5052543/how-to-fire-ajax-request-periodically
function periodic_buttonstatus () {
// periodischer Aufruf zum Holen des Buttonstatus
  $.ajax ({
      url: "/getinfo/buttonstatus", 
      success: function(data){
      var statusarray = $.parseJSON(data);
      var i;
      for (i = 0; i < statusarray.length; i++){
          buttonStatus(i, statusarray);
      }
      },
      complete: function () {
      setTimeout (periodic_buttonstatus, 1000);
      }
  }); // ende $.ajax
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
              makeCueAttribSlider (heads[i], attribs[i], levels[i],
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


function makeCueAttribSlider (head, attrib, level, url) {
  // Slider fürs Cue-Edit erzeugen
  // siehe: cuefader.html, stage.html
  // console.log ("makeCueAttribSlider:" + head +" "+ attrib +" "+ level);
  $('#attrib-'+head+attrib)
      .slider({
          orientation:"vertical",
          range: "min",
          value:level,
          min: 0,
          max:255,
          slide: function (event, ui){
              //console.log (attrib + ": level: " + ui.value);
              var args = {head:head, attrib:attrib, level:ui.value};
              $.post (url, args);
              $("#sessiondata").attr ("topcuecontent", "true");
          }
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
function periodic_commonstatus () {
  // periodischer Aufruf zum Holen der variablen Basisdaten
    $.ajax ({
        url: "/getinfo/commonstatus", 
        success: function(data){
          var jdata = JSON.parse (data);
          //console.log ("common: " + JSON.stringify (jdata));
          if (jdata["editmode"] == "select") {
            setEditmode ("select");
          } else {
            setEditmode ("edit");
          };
          initMouseMode ();
          if (jdata["topcuecontent"] == "true") {
            showSecondNav ();
          } else {
            hideSecondNav ();
          } 

        },
        complete: function () {
        setTimeout (periodic_commonstatus, 1000);
        }
    }); // ende $.ajax
  }



// --- Navigation für Topcue und CSV-Buttons: --------------------------------

$(document).ready (function() {

  periodic_commonstatus ();
  // Mousemode Optionen:
  changeMousemode (".mousemode-edit", "edit");
  changeMousemode (".mousemode-select", "select");

  // topcue Nav Anzeige auf allen Seiten:
  if ($("#sessiondata").attr ("topcuecontent") == "true") {
    showSecondNav ();
  } else {
    hideSecondNav ();
  };

  $(".selectDiv").empty();
  //modaldialogToPython (".cueview", "/cuechild/cuemodal");
  modaldialogToPython ("#showCueModal", "/cuechild/cuemodal");
  modaldialogToPython (".topview", "/cuechild/topview");
  filedialogToPython  (".topsavecue", "/cuechild/topsave/cue");
  modaldialogToPython  (".topsavefader", "/cuechild/topsave/fader");
  modaldialogToPython  (".topsavebutton", "/cuechild/topsave/button");
  modaldialogToPython  (".topsavecuelist", "/cuechild/topsave/cuelist");
});