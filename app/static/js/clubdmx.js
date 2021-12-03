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
// ----------------------------------------------------------------------------
// Mousemode ändern: mögliche Werte: 'edit', 'select'
var MouseModeStr;

function changeMousemode (id, newmode) {
  $(id).on ("click", function () {
    $.get ("/editmode/"+newmode, function (data) {
      $(".edit-select-button").text (data);
      $("#sessiondata").attr ("editmode", newmode);
      MouseModeStr = newmode;
      initMouseMode ();
    });
  }); 
}

function initCsvtableMouse () {
  // Verhalten bei Click in CSV-Tabelle:
  if (editmode ("select")) {
    selectableCsvLines ();
  } else if (editmode ("edit")) {
    $("tr").removeClass ("ui-state-highlight");
    removeSelectableCsvLines ();
    editableCsvFields ();
    // Buttons:
    $(".navSelect").addClass ("d-none");
    $(".csvClipboard").addClass ("d-none"); 
  }
}

function initMouseMode () {
  // wird in der jeweiligen html-Seite neu definiert
  initCsvtableMouse ();
  // console.log ("Maus: nothing to do.");
}


// CELL-EDIT start
var editcell = undefined; // zu editierende Text-Zelle

function editmode (str) {
  // prüfen, welcher editmode eingeschalten ist
  // mögliche Werte: edit, select=default
  // if ( $("#sessiondata").attr ("editmode") == str) {
  if ( MouseModeStr == str) {
      return true;
  } else {
    return false;
  };
};
    
    
// highlight edit-cell 
function selectTextcell() {
  if ( editmode ("edit") ) {
    editcell.attr ('contenteditable', 'true')
      .addClass('edit_selected')
      .focus();
  };
};
    
//---> save after ENTER > start
$(document).keydown(function (event){
  if ( event.which == 13 ) {  // enter
    event.preventDefault();
    editcell.blur();
  // } else if ( event.which == 27 ) { // ESC
  //   editcell.blur ();
  //   editcell = undefined;
  };
}); //---> save after ENTER > end  

// cell Daten in array schreiben:
function get_celldata (cell) {
  var table    = cell.closest("table");
  if (table.length == 0) {
      table = cell.closest (".csvfile");
  };
  var filename = table.attr("file");
  var filepath = table.attr ("pluspath");
  var option   = table.attr("option");
  var file;
  if (filepath) {
      file = filepath + '+' + filename;
  } else {
      file = filename;    
  };
  
  var col_num = cell.attr('col_num');
  var row_num = cell.attr('row_num');
  var text = cell.contents().filter(function() {
                  return this.nodeType == Node.TEXT_NODE;
              }).text().trim();
  var arr = {file:file, row_num:row_num, col_num:col_num, text:text };
  if (option != undefined) {
      //console.log (option);
      $.extend(arr, {option:option});
  };
  return arr;
};

//-->save cell data > start
function saveCell () {
    var arr = get_celldata (editcell);
    editcell
      .removeClass('edit_selected') //add bg css
      .html (arr.text);
    editcell = undefined;
    // an Server schicken:
    $.post ('/csv/savecell', arr, function (data) {
      if (data != "ok") {
        location.reload (); // Fehler anzeigen
      } else {
        $(".csvchanges").removeClass ("d-none"); // Buttons anzeigen
      }

    });
};     //-->save cell data > end

// createSelectOptions:
// Optionen für Select-Feld erzeugen
function createSelectOptions (values, current) {
  let optionHTML = "<select id='cell_selector' class='form-control'>";
  //console.log ("Attribs: " + attribs);
  for (let att of values) {
    if (att == current) {
      optionHTML += "<option selected='selected' value='" 
                    + att + "'>" + att + "</option>"
    } else {
      optionHTML += "<option value='" + att + "'>" 
                    + att + "</option>"
    };
  };
  optionHTML += "</select>";
  return optionHTML;
};

function editableCsvFields () {
  // select-Buttons entfernen:
  $(".navSelect").addClass ("d-none");
  $(".csvClipboard").addClass ("d-none"); 

  // csv-Felder editierbar machen, nach Feldname unterscheiden:
  $(".csvcell").click (function (event) {
    if (editcell == undefined && editmode ("edit")) {
      event.preventDefault ();
      editcell = $(this);
      let celldata = get_celldata (editcell);
  
      let args = {subdir:celldata.option }; // für /getinfo/layout
      args.row_num = celldata.row_num;
      args.col_num = celldata.col_num;
      // fieldname steht in Table-Header Zeile an gleicher Position:
      let fieldname = $("th").filter ( $("*[col_num='" + args.col_num + "']"))
       .text().trim().toLowerCase();
      args.field = fieldname;
  
      let current = celldata.text;
      
      $.get ("/getinfo/layout", args, function(data) {
        var layout = $.parseJSON (data);

        // unterscheiden nach type:
        if (layout.type == "list") {   // Auswahl-Liste:
          let optionHTML = createSelectOptions (layout.values, current);
          editcell.html (optionHTML);
          $("#cell_selector").focus ();
  
          $("#cell_selector").focusout ( function () {
            let result = $("#cell_selector").val ();
            celldata.text = result;
            editcell.html (result);
            editcell = undefined;
            $.post ('/csv/savecell', celldata);
          });
    
        } else if (layout.type == "file") { // File
          if ("option" in celldata) {
              //console.log ("Option vorhanden.");
              celldata.option = layout.subdir;
          } else {
              $.extend(celldata, {option:layout.subdir});
          };
          filedialogToPython (editcell, "/csv/filename", celldata);

        } else if (layout.type == "disabled") { 
          editcell = undefined;

        } else if (layout.type == "headattr") {  // Head-Attribut
          // Spalte von HeadNr ermitteln:
          var headcol, text;
          $("#csvtable th").each (function () {
            text = $(this).text().trim().toLowerCase();
            if (text == "headnr") {
              headcol = $(this).attr ("col_num");
              var headnr = editcell.siblings("[col_num='" + headcol + "']").text().trim();
              $.get ("/getattribs/"+headnr, function (data) {
                var attribs = $.parseJSON (data);
                // ab hier gleich wie layout.type == 'list'
                let optionHTML = createSelectOptions (attribs, current);
                editcell.html (optionHTML);
                $("#cell_selector").focus ();
        
                $("#cell_selector").focusout ( function () {
                  let result = $("#cell_selector").val ();
                  celldata.text = result;
                  editcell.html (result);
                  editcell = undefined;
                  $.post ('/csv/savecell', celldata);
                });
              });
            };
          });

        } else { // Text
          selectTextcell ();
        };
    });
  
  };

  });
}

$(document).ready (function() {

  // MouseMode initialisieren:
  MouseModeStr = $("#sessiondata").attr ("editmode");

  // editcell leeren:
  editcell = undefined
  //--->save single field data > start
	$(document).on('focusout', '.edit_selected', function(event) {
        if (editcell == undefined) {
            alert ("focusout, editcell undefined!");
        } else {
            event.preventDefault();
            saveCell();
        };
	});	
	//--->save single field data > end
    
}); // ende document ready function
// CELL EDIT Ende

// --- Topcue Navigation anzeigen/verbergen ---------------------------------
function resizeStage () {
  // wird in stage.js neu definiert
  console.log ("Resize:nothing to do");
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


// --- Selectable -----------------------------------------------------------
// Sichtbarkeit der Buttons:
// Elemente ausgewählt: Buttons mit class navSelect sichtbar: cut, copy
// Elemente im Clipboard: Buttons mit class csvClipboard sichtbar: paste, clear

function postSelectedRows ($selectees) {
  // ausgewählte Elemente ins Clipboard aufnehmen
  var rows = "";
  selected = $selectees.filter( ".ui-selected" ).toArray();
  var i, num;
  for (i = 0; i< selected.length; i++) {
    num = $(selected[i]).attr("row_num");
    rows = rows + num + ' ';
  };
  if (i > 0) {
      $(".csvClipboard").removeClass ("d-none");    
  }
  $.post ("/csv/selected_rows", {rows:rows} );
  return i;
}

function csvClipboard () {
  // selektierte Reihen im Clipboard ?
  // return: true oder false
  var data = $("#sessiondata").attr ("csvclipboard");
  if (data.length) {
      return true;
  } else {
      return false;
  };
}

function selectableCsvInit () {
  // Buttons initialisieren
  // cut/copy Buttons:
  $(".navSelect").addClass ("d-none");
  // paste/clear Buttons:
  if (csvClipboard ()) {
      $(".csvClipboard").removeClass ("d-none");  
  } else {
      $(".csvClipboard").addClass ("d-none");  
  }
}

function selectableButtonUpdate ($sel) {
  // cut/paste/copy/clear Buttons anzeigen/verbergen

  var widget = $sel.data( "uiSelectable" );
  var num = postSelectedRows ( widget.selectees );
  // cut/copy Button:
  if (num > 0) {
      $(".navSelect").removeClass ("d-none");
  } else {
      $(".navSelect").addClass ("d-none");
  }
  // paste/clear Buttons:
  if (csvClipboard ()) {
      $(".csvClipboard").removeClass ("d-none");  
  } else {
      $(".csvClipboard").addClass ("d-none");  
  }
}

var selectableCsvLinesEnabled = false;
function selectableCsvLines () {
  // 
  if (! selectableCsvLinesEnabled) {
    selectableCsvLinesEnabled = true;
    selectableCsvInit ();
    // if (editmode ("select")) {
  
    $("#csvtable > tbody").selectable ({
      filter:"tr",
      create: function( e, ui ) {
          postSelectedRows ( $() );
      },
  
      selected: function( e, ui ) {
          if ($(ui.selected).hasClass('ui-state-highlight')) {
              $(ui.selected).removeClass('ui-state-highlight')
                            .removeClass('ui-selected');
          } else {            
              $(ui.selected).addClass('ui-state-highlight')
                            .addClass('ui-selected');
          }  
          // selectableButtonUpdate ($(this));
      },
  
      unselected: function( e, ui ) {
          $( ui.unselected ).removeClass( "ui-state-highlight" );
          // selectableButtonUpdate ($(this));
      },
      stop: function (e, ui) {
        selectableButtonUpdate ($(this));  
      }
      
    });
  
    // }; // end if editmode select
  
  }
}

function removeSelectableCsvLines () {
  // selectable entfernen
  if (selectableCsvLinesEnabled) {
    selectableCsvLinesEnabled = false;
    $("#csvtable > tr").removeClass('ui-state-highlight')
      .removeClass('ui-selected');
    $("#csvtable > tbody").selectable ("destroy");

  }
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
    event.preventDefault ();
    event.stopPropagation ();

    var filename = $(this).attr ("name")

    $.get({
      url: "/cue/cuedetails", 
      data: {filename:filename},
      cache: false })
      .then ( function(data){
        modaldata = $.parseJSON(data);
        // console.log ("modaldata: " + modaldata);
        $("#dialogModal").html (modaldata);
        $("#viewModal").modal();

        // Editierbar machen:
        initCsvtableMouse ();

        $("#viewModal").on ("hide.bs.modal"), function () {
            if (fileDialogParams.select=='true') {
                saveCell ();
            };
        };
        //$("#fileselect").show ();
        $("#viewModal").on ("hidden.bs.modal", function () {
          postSelectedRows ( $() ); // selektierte Reihen löschen
          location.reload ();
        });
      });
  }); // ende $ fileview

  // --- Cue-Auswahl:
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

// --- Navigation für Topcue und CSV-Buttons: --------------------------------

$(document).ready (function() {
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
});