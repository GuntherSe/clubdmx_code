// stage.js
// Verwendung in stage.html und stage_mobil.html

function resizeStage () {
  // Breite: 100%

  var bodyheight = $("body").height() ;
  var navheight; 
  var headerheight = $("#headercontainer").outerHeight();
  if ($("#secondNav").css ("display")=="none") {
    navheight = $("#primaryNav").outerHeight () ;
  } else {
    navheight = $("#nav-container").outerHeight () + 2; 
  };
  var stbuttonheight = $(".stage-buttons").outerHeight();
  var resizeheight = bodyheight - headerheight - navheight - stbuttonheight -20;

  $(".stage").height (resizeheight);
  // console.log ("resizeStage: "+ resizeheight);
}

// Resizeable mit Fenserbreite verändern:
$(window).on('resize', function(){
  resizeStage ();
});

// --- editierbare <div> -----------------------------------------------------------
// https://stackoverflow.com/questions/2441565/how-do-i-make-a-div-element-editable-like-a-textarea-when-i-click-it/4179909
function divClicked() {
  var divHtml = $(this).html();
  var classlist = $(this).attr('class');
  //console.log ("classlist: "+classlist);
  var editableText = $("<textarea />").attr ('class', classlist);
  editableText.val(divHtml).removeClass ("emptybox");
  var width = $(this).parent().width ();
  //console.log ("Breite: " + width);
  editableText.width ( width );
  editableText.height ("2rem");
  $(this).replaceWith(editableText);
  editableText.focus();
  // setup the blur event for this new textarea
  editableText.blur(editableTextBlurred);
}

function editableTextBlurred() {
  var html = $(this).val();
  var classlist = $(this).attr('class');
  var viewableText = $("<div>").attr ('class', classlist);
  viewableText.html(html);
  if (viewableText.is (":empty")) {
      viewableText.addClass ("emptybox");
  };
  $(this).replaceWith(viewableText);
  // Daten in csv-Tabelle schreiben:
  var data = {};
  var row_num = viewableText.parent().attr ("row_num");
  //console.log ("row_num: " + row_num);
  // data ist verschachteltes array, um kompatibel mit selectables zu sein
  var item = {};
  item["row_num"] = row_num;
  // welches Feld wurde editiert?
  if (classlist.includes ("itemText")) {
      item["Text"] = html;
  } else if (classlist.includes ("itemName")) {
      item["Name"] = html;
  } else if (classlist.includes ("itemComment")) {
      item["Comment"] = html;
  };
  data["1"] = item;
  $.get ("/stage/update_item", {"data":JSON.stringify (data)});
  // setup the click event for this new div
  viewableText.click(divClicked);
  $(".csvchanges").removeClass ("d-none"); // Buttons anzeigen
}

// --- Maus-Verhalten --------------------------------------------------------
function initStageMouse () {
  // Stage:
  if (editmode ("select")) {
    // console.log ("Stage-Maus: select");
    selectableStageElements ();
    $(".stage").css ("border-color", "orange");
    $("div.edit_div").removeClass ("emptybox").off ();

  } else if (editmode ("edit")) {
    // console.log ("Stage-Maus: edit");
    removeSelectableStage ();
    $("div.edit_div").click (divClicked);
    $("div.edit_div").each (function () {
      if ($(this).is (":empty")) {
        $(this).addClass ("emptybox");
      };
    });
    $(".stage").css ("border-color", "lightblue");
    // Buttons:
    $(".navSelect").addClass ("d-none");
    $(".csvClipboard").addClass ("d-none"); 
  };
}

function initMobStageMouse () {
  // Stage:
  if (editmode ("select")) {
    console.log ("Stage-Maus: select");
    selectableMobileElements ();
    $(".mob-stage").css ("border-color", "orange");
    $("div.edit_div").removeClass ("emptybox").off ();

  } else if (editmode ("edit")) {
    console.log ("Stage-Maus: edit");
    removeSelectableStage ();
    $("div.edit_div").click (divClicked);
    $("div.edit_div").each (function () {
      if ($(this).is (":empty")) {
        $(this).addClass ("emptybox");
      };
    });
    $(".mob-stage").css ("border-color", "lightblue");
    // Buttons:
    $(".navSelect").addClass ("d-none");
    $(".csvClipboard").addClass ("d-none"); 
  };
}


// --- Selectable -------------------------------------------------------------

var selectableStageEnabled = false;
function selectableStageElements () {
  // Funktionalität für draggables, resizeables 
  // wie bei csv Tabellen: cut/paste
  var delta_x, delta_y, start_x, start_y, tmppos;
  var delta_w, delta_h, start_w, start_h;
  var stageleft, stagetop; 
  var newwidth, newheight, tmpw, tmph;
  var rownum; // Identifizierung des Verschiebe-Elements (bei mehreren Elementen)
  if (! selectableStageEnabled ) {
    selectableStageEnabled = true;
    selectableCsvInit ();
  
    $("#csvtable").selectable ({
      filter: ".stage-element",
      create: function( e, ui ) {
        postSelectedRows ( $() );
      },

      selected: function( event, ui ) {
        $(ui.selected).addClass('highlight')
        .addClass('ui-selected')
        .resizable({containment: "#csvtable", 
          minWidth: 30, minHeight:30,
          start: function () {
            // stageleft = $("#csvtable").scrollLeft ();
            // stagetop = $("#csvtable").scrollTop ();
            // console.log ("StageW: "+stageleft+", H: "+stagetop);
            delta_w = 0;
            delta_h = 0;
            // console.log ("ParseW: "+this.style.width+", H: "+this.style.height);
            start_w = $(this).outerWidth(true);
            start_h = $(this).outerHeight(true);
            // console.log ("StartW: "+start_w+", H: "+start_h);
          },
          resize: function () {
            // Größe berechnen:
            
            newwidth  = $(this).outerWidth(true);
            newheight = $(this).outerHeight(true);
            // console.log ("W: "+newwidth+", H: "+newheight);
            delta_w = newwidth - start_w;
            delta_h = newheight - start_h;
            start_w = newwidth;
            start_h = newheight;
            // console.log ("delta: "+delta_w+", "+delta_h);
            // Größe ändern:
            $(".highlight").each ( function () {
              tmpw = Math.max (30, $(this).outerWidth(true) + delta_w) ;
              tmph = Math.max (30, $(this).outerHeight(true) + delta_h) ;
              // console.log ("newwidth: "+tmpw+" height: "+tmph);
              $(this).css ({"width": tmpw, "height": tmph});
            }) ;
          },
          stop: function( event, ui ) {
            var data = {};
            var item;
            $(".highlight").each (function (index) {
              item = {};
              item ["row_num"] = $(this).attr ("row_num");
              item ["Width"]   = $(this).outerWidth(true);
              item ["Height"]  = $(this).outerHeight(true);
              data[index.toString()] = item;
            });
            // console.log ("Data: "+JSON.stringify (data));
            $.get ("/stage/update_item", {"data":JSON.stringify (data)});
            // Buttons anzeigen:
            $(".csvchanges").removeClass ("d-none"); 
          }
        })
        .draggable({
          containment: "#csvtable", 
          scroll:true,
          start: function () {
            // stageleft = stage.left;
            stagetop = $("#csvtable").scrollTop ();
            stageleft = $("#csvtable").scrollLeft ();
            // console.log ("Stage:"+stagetop+", "+stageleft);
            delta_x = 0;
            delta_y = 0;
            tmppos = $(this).position ();
            start_x = tmppos.left;
            start_y = tmppos.top;
            console.log ("Start L: "+start_x+", T: "+start_y);
            rownum = $(this).attr ("row_num");
          },
          drag: function () {
            // Verschiebung berechnen:
            var newleft, newtop;
            var dleft, dtop; //dragged element

            stagetop = $("#csvtable").scrollTop ();
            stageleft = $("#csvtable").scrollLeft ();
            // console.log ("Stage:"+stagetop+", "+stageleft);

            tmppos = $(this).position ();
            dleft = tmppos.left;
            dtop  = tmppos.top;
            // console.log ("Drag-L: "+dleft+" T: "+dtop 
            //   +" offL:"+doffleft+" offT:"+dofftop);
            delta_x = Math.round (dleft - start_x) ;
            delta_y = Math.round (dtop - start_y) ;
            start_x = dleft;
            start_y = dtop;
            // console.log ("delta: "+delta_x+" "+delta_y);

            // verschieben:
            $(".highlight").each ( function () {
              if ($(this).attr ("row_num") != rownum) {
                // die anderen Elemente verschieben:
                tmppos = $(this).position ();
                newleft = tmppos.left + delta_x + stageleft;
                newtop  = tmppos.top  + delta_y + stagetop;
                // console.log ("Each L:"+newleft+" T:"+newtop );
                $(this).css ({"left": newleft, "top": newtop});
              };
            }) ;

          },
          stop: function () {
            var data = {};
            var item;
            // Auswahl verschieben:
            $(".highlight").each (function (index) {
              tmppos = $(this).position ();
              item = {};
              item ["Left"] = Math.round (tmppos.left+stageleft);
              item ["Top"]  = Math.round (tmppos.top+stagetop);
              item ["row_num"] = $(this).attr ("row_num");
              data[index.toString()] = item;

              // console.log ("Data:" + item["Left"] + ","+ item["Top"] 
              //   + "," + item["row_num"]);
            });
            $.get ("/stage/update_item", {"data":JSON.stringify (data)});
            // Buttons anzeigen:
            $(".csvchanges").removeClass ("d-none"); 
          }
        });
        selectableButtonUpdate ($(this));
      },
      unselected: function( e, ui ) {
        $( ui.unselected ).removeClass("highlight")
          .draggable ("destroy")
          .resizable ("destroy");
        //resizeStage ();
        var content = $("#sessiondata").attr ("topcuecontent");
        //console.log ("topcue: "+ content);
        if (content == "false") {
            hideSecondNav ();
        };
        selectableButtonUpdate ($(this));
      }
    }); // ende selectable
  }; // endif
}

function removeSelectableStage () {
  // selectable entfernen:
  if (selectableStageEnabled) {
    selectableStageEnabled = false;
    $(".stage-element").off ()
      .removeClass("ui-selected highlight")
      .removeClass ("ui-resizable ui-draggable ui-draggable-handle") ;
    $(".ui-resizable-handle").remove ();
    $("#csvtable")
    .removeClass ("ui-selectable").selectable ("destroy");
      
  }
}


function selectableMobileElements () {
  if (! selectableStageEnabled ) {
    selectableStageEnabled = true;

  selectableCsvInit ();
  // if (editmode ("select")) {
    $("#csvtable").selectable ({
      filter: ".mobil-element",
      // cut/paste fehlerhaft durch Sortierung der Widgets
      // daher nicht implementiert
      selected: function( event, ui ) {
        if ($(ui.selected).hasClass('highlight')) {
          $(ui.selected).removeClass('highlight ui-selected');
          var content = $("#sessiondata").attr ("topcuecontent");
          //console.log ("topcue: "+ content);
          if (content == "false") {
              hideSecondNav ();
          };
        } else {            
          $(ui.selected).addClass('highlight ui-selected');
        };
      },
      unselected: function( e, ui ) {
        $( ui.unselected ).removeClass("highlight");
        var content = $("#sessiondata").attr ("topcuecontent");
        //console.log ("topcue: "+ content);
        if (content == "false") {
            hideSecondNav ();
        };
      }
    }); // ende selectable
  }; // endif
}
// --- Head-Slider erzeugen: -------------------------------------------------
// für die Selektion Slider erzeugen: alle row_num's an Server schicken
// dort für alle Attribute Sammel-Slider erzeugen und retournieren

var selectedHeads;

function headsInSelection () {
  // alle Headnummer einer Selektion in selectedHeads anfügen
  var headnr;
  var selected = $(".highlight.head");
  //console.log ("selectablestop: "+ selected.length);
  if (selected.length) {
    $(selected).each (function () {
      headnr = $(this).children (".itemName").text ().trim ();
      selectedHeads  = selectedHeads + headnr + " " ;
    });
  };
}

function headsInSelectedGroups () {
  // alle Headnummern der selektierten Gruppen 
  var headnr;
  $(".highlight.gruppe").each (function () {
    headnr = $(this).children (".itemComment").text ().trim ();
    selectedHeads  = selectedHeads + headnr + " " ;
  })
}

function selection_headslider () {
  // zu selectedHeads Attributslider erzeugen
  showSecondNav ();
  // console.log ("Selektion: " + selectedHeads);
  // Headfader vom Server holen:
  var args = {heads:selectedHeads};
  $.get ("/stage/headfader", args, function (data) {
    var jdata = JSON.parse (data);
    if (jdata != "false") {
      //$(".selectDiv").html ("Selektion:" + selectedHeads);
      // alert (jdata["table"]);
      $("#showModal").trigger ("click");
      $("#dialogModal").on ("shown.bs.modal", function () {
        var heads      = jdata["heads"];
        var attribs    = jdata["attribs"];
        var levels     = jdata["levels"];
        var headstring = jdata["headstring"];
        $(".selectDiv").html ("Selektion: " + headstring);
        $("#faderspace").html (jdata["table"]);
        // console.log ("Levels: " +JSON.stringify (levels));
        for (var i=0; i < attribs.length; i++){
            makeCueAttribSlider (heads[i], attribs[i], 
                levels[attribs[i]], '/stage/headfader' );
        };
      }) ;
    };
  });
}


function periodic_attribstatus () {
  $.ajax ({
    url: "/getinfo/firstattribute", 
    success: function(data){
      var attlevels = $.parseJSON(data);
      var cssclass;
      for (var key in attlevels) {
        cssclass = ".head-" + key;
        $(cssclass).css ("width", attlevels[key]);
      }
    },
    complete: function () {
      setTimeout (periodic_attribstatus, 1000);
    }
  }); // ende $.ajax 
}

// ----------------------------------------------------------------------------

$(document).ready ( function () {  
  // initStageMouse ();
  resizeStage ();

  $(".stage, .mob-stage").on ("selectablestop", function( ) { 
    selectedHeads = "";
    headsInSelection ();
    headsInSelectedGroups ();
    if (selectedHeads.length) {
      selection_headslider ();
    };
  });
  
  // --- Stage-Buttons: ----------------------------------------------------
  filedialogToPython (".openButton", "/csv/open", {"option":"stage"});
  filedialogToPython (".saveasButton", "/csv/saveas", {"option":"stage"});

  modaldialogToPython ("#showModal", "/stage/headmodal");

}); // ende document ready

