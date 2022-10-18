// csvedit.js: Sammlung von JS-Funktionen zur Verarbeitung von CSV-Dateien

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
    // $("tr").removeClass ("ui-state-highlight");
    removeSelectableCsvLines ();
    editableCsvFields ();
    // Buttons:
    $(".navSelect").addClass ("d-none");
    $(".csvClipboard").addClass ("d-none"); 
  }
}

function initMouseMode () {
  // kann in der betreffenden html-Seite neu definiert werden.
  // speziell: stage.html und stage-mobil.html
  initCsvtableMouse ();
}

// ----------------------------------------------------------------------------
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
  if (editcell != undefined) {
    if ( event.which == 13 ) {  // enter
      event.preventDefault();
      editcell.blur();
    };
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
  // values: Liste
  // current: aktuelles Element
  // return: HTML code für Listenauswahl
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

        } else if (layout.type == "head") { // Head in Cue-Zeile:
          $.get ("/getheads", function (data) {
            var heads = $.parseJSON (data);
            // ab hier gleich wie layout.type == 'list'
            let optionHTML = createSelectOptions (heads, current);
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
        } else if (layout.type == "command") {
          $.get ("/getinfo/commands", function (data) {
            var attribs = $.parseJSON (data);
            // wieder wie layout.type == 'list
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
    selectableCsvInit ();
    if (! selectableCsvLinesEnabled) {
      selectableCsvLinesEnabled = true;
    };

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
    
    
    // }
  }
  
  function removeSelectableCsvLines () {
    // selectable entfernen
    if (selectableCsvLinesEnabled) {
      selectableCsvLinesEnabled = false;
      if ($("#csvtable > tbody").hasClass ("ui-selectable")) {
        $("#csvtable > tr").removeClass('ui-state-highlight ui-selected');
        $("#csvtable > tbody").selectable ("destroy");
      };
      // if ($("#csvtable > tbody").selectable ("instance") != undefined) {
      //   $("#csvtable > tbody").selectable ("destroy");
      // };
  
    }
  }
  