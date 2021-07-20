// stage.js
// Verwendung in stage.html und stage_mobil.html

function resizeStage () {
  // Stage-Breite abhängig von den Stage-Elementen: 
  // Breite: max (left+width), Höhe: max (top+height)
  var resizewidth = 0, resizeheight = 0;
  var position, right, height, screenheight;
  $(".stage-element").each ( function () {
    position = $(this).position ();
    right = Math.abs (position.left) + $(this).width ();
    height = Math.abs (position.top) + $(this).height ();
    if (right > resizewidth) {
        resizewidth = right;
    }
    if (height > resizeheight) {
        resizeheight = height;
    }
  });
  resizewidth = Math.max (resizewidth+20, $("#maincontainer").width());

  var bodyheight = $("body").height() ;
  var headerheight = Math.max ( $(".header-container").height(), $("#workspace").height() );
  // var menuheight = $(".menuheight").height();
  var navheight = $("#primaryNav").height();
  if ($("#sessiondata").attr ("topcuecontent") == "true") {
      navheight = navheight + $("#secondNav").height();
  } 
  var stbuttonheight = $(".stage-buttons").height();
  var screenheight = bodyheight - headerheight - navheight - stbuttonheight -20;
  resizeheight = Math.max (resizeheight+20, screenheight);

  $(".stage").width (resizewidth);
  $(".stage").height (resizeheight);
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
  console.log ("row_num: " + row_num);
  data["row_num"] = row_num;
  if (classlist.includes ("itemText")) {
      data["Text"] = html;
  } else if (classlist.includes ("itemName")) {
      data["Name"] = html;
  } else if (classlist.includes ("itemComment")) {
      data["Comment"] = html;
  };
  $.get ("/stage/update_item", data);
  // setup the click event for this new div
  viewableText.click(divClicked);
  $(".csvchanges").removeClass ("d-none"); // Buttons anzeigen
}

$(document).ready(function() {
  // Stage-Rahmen einfärben, div editierbar machen:
  if ( editmode ("edit")) {
    $("div.edit_div").click (divClicked);
    $(".stage, .mob-stage").css ("border-color", "lightblue");
    $("div.edit_div").each (function () {
        if ($(this).is (":empty")) {
            $(this).addClass ("emptybox");
        };
    });
  } else if (editmode ("select")) {
    $(".stage, .mob-stage").css ("border-color", "orange");
  };

});
// --- Selectable -------------------------------------------------------------

function selectableStageElements () {
  // Funktionalität für draggables, resizeables 
  // wie bei csv Tabellen: cut/paste
  selectableCsvInit ();
  if (editmode ("select")) {
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
                    stop: function( event, ui ) {
                      var row_num = $(this).attr ("row_num");
                      var data = {};
                      let str = this.style.width;
                      data ["Width"]   = extract_int (str);
                      str = this.style.height;
                      data ["Height"]  = extract_int (str);
                      data ["row_num"] = row_num;
                      $.get ("/stage/update_item", data);
                      $(".csvchanges").removeClass ("d-none"); 
                      // Buttons anzeigen
                    }
        })
        .draggable({containment: "#csvtable", 
                    scroll:true,
                    stop: function( event, ui ) {
                      var row_num = $(this).attr ("row_num");
                      var data = {};
                      let str = this.style.left;
                      data ["Left"]    = extract_int (str);
                      str = this.style.top;
                      data ["Top"]     = extract_int (str);
                      data ["row_num"] = row_num;
                      $.get ("/stage/update_item", data);
                      $(".csvchanges").removeClass ("d-none"); 
                      // Buttons anzeigen
                  }
          });
          selectableButtonUpdate ($(this));
      },
      unselected: function( e, ui ) {
          $( ui.unselected ).removeClass("highlight")
                              .draggable ("destroy")
                              .resizable ("destroy");
          $(".selectDiv").empty();
          $("#workspace").empty ();
          resizeStage ();
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

function selectableMobileElements () {
  selectableCsvInit ();
  if (editmode ("select")) {
    $("#csvtable").selectable ({
      filter: ".mobil-element",
      // cut/paste fehlerhaft durch Sortierung der Widgets
      // daher nicht implementiert
      selected: function( event, ui ) {
        if ($(ui.selected).hasClass('highlight')) {
          $(ui.selected).removeClass('highlight ui-selected');
          // do unselected stuff
          $(".selectDiv").empty();
          $("#workspace").empty ();
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
        $(".selectDiv").empty();
        $("#workspace").empty ();
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
function selection_headslider (selection) {
  var selectedHeads = "";
  showSecondNav ();
  // Headnr:
  $(selection).each (function () {
    headnr = $(this).children (".itemName").text ().trim ();
    // console.log ("Head: " + headnr);
    selectedHeads  = selectedHeads + " " + headnr;
  });
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
      $(".selectDiv").html ("Selektion:" + selectedHeads);
      $("#faderspace").html (jdata["table"]);
        var heads   = jdata["heads"];
        var attribs = jdata["attribs"];
        var levels  = jdata["levels"];
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
  resizeStage ();
  $(".stage, .mob-stage").on ("selectablestop", function( ) { 
    var selected = $(".highlight.head");
    //console.log ("selectablestop: "+ selected.length);
    if (selected.length) {
      selection_headslider (selected);
    };
  });

  // --- Stage-Buttons: ----------------------------------------------------
  filedialogToPython (".openButton", "/csv/open", {"option":"stage"});
  filedialogToPython (".saveasButton", "/csv/saveas", {"option":"stage"});

  modaldialogToPython ("#showModal", "/stage/headmodal");

}); // ende document ready

