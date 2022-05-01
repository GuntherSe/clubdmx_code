/* File Dialog        
Modal erzeugen: am Server /filedialog/<params>
Datei auwählen: explore
Ergebnis: var result
result hat '+' statt '/'
*/
var fileDialogParams = {};   // Startparameter
/*
    hier zu finden:
    insert_str: 'explore' (default) eindeutiger Punkt im DOM (ohne '#')

    basedir:   Pfad beim ersten Aufruf von explore
    spath:     Suchpfad, Unterordner von basedir oder absolut-Pfad
    ftype:     File Endung
    updir:     'false' (default) oder 'true' - '..' anzeigen

    select:    'false' (default) oder 'true' - Datei wurde ausgewählt
    result:    ausgewählte Datei (voller Pfad)
    filepath:  aktueller Pfad im Resultat
    filename:  Datei ohne Pfad
*/
function filedialogToPython (clickid, url, args) {
    // bei Klick auf clickId wird filedialog aufgerufen:
    // Modaldaten werden geholt
    // mit Drücken des selectButton werden die Daten
    // an Server gepostet, anschließend: location.reload
    $(clickid).on ("click", function (event) {
        // event.preventDefault ();
        //savecellReload = false;
        //console.log ("args: " + JSON.stringify (args));
        $.get (url, args, function (data){

            var result = {};
            var modalData = JSON.parse (data);
            //console.log ("fdToPython: " + data);
            modalData.insert_str = "modalexplore";
            getFDparams (modalData);

            $("#dialogModal").html (modalData.dialogbox);
            $("#viewModal").modal();
            fileExplore (fileDialogParams);
    
            // Auswertung beim Schließen:
            $("#viewModal").on ('hidden.bs.modal', function(){
                // console.log ("sp:" + JSON.stringify(fileDialogParams));

                var fn = $("#filename").first().val();
                if (fileDialogParams.select=='true') {
                  result.args = JSON.stringify (args);  
                  result.path =  JSON.parse (JSON.stringify (fileDialogParams.filepath));
                  if (fn.length){
                    result.filename  = fn;
                    result.shortname = fn.replace (/\.[^/.]+$/, "");
                    // https://stackoverflow.com/questions/4250364/how-to-trim-a-file-extension-from-a-string-in-javascript
                  } else {
                    // nur Pfad ausgewählt
                    result.filename  = "";
                    result.shortname = "";
                  }
                  $.post (url, result, function (){
                    location.reload ();
                    return;
                  });
                } else { 
                    location.reload ();
                    return;
                };
            });
            $(".close-modal").on ("click", function(){
                //console.log ("Modal close");
                $.post ("/forms/modalclose");
            });
        
            // selectbutton aktivieren, Unterscheidung close und select:
            $("#selectButton").on ('click', function(){
                fileDialogParams.select = 'true';
            });
        });
    
    });
};
    

function fileDialog (args, callback) {
    getFDparams (args);
    $.get ("/filedialogbox", args, function (data){

        var result = {};
        var modalData = JSON.parse (data);
        fileDialogParams.insert_str = "modalexplore";

        $("#dialogModal").html (modalData);
        $("#viewModal").modal();
        fileExplore (fileDialogParams);

        // Auswertung beim Schließen:
        $("#viewModal").on ('hidden.bs.modal', function(){
            // console.log ("sp:" + JSON.stringify(fileDialogParams));
            var fn = $("#filename").first().val();
            if (fileDialogParams.select=='true') {
              result.path =  JSON.parse (JSON.stringify (fileDialogParams.filepath));
              if (fn.length){
                result.filename  = fn;
                result.shortname = fn.replace (/\.[^/.]+$/, "");
                // https://stackoverflow.com/questions/4250364/how-to-trim-a-file-extension-from-a-string-in-javascript
              } else {
                // nur Pfad ausgewählt
                result.filename  = "";
                result.shortname = "";
              }
              callback (result)  ;
              return;
            };
        });
        $("#selectButton").on ('click', function(){
            fileDialogParams.select = 'true';
        });
    });
};

function getFDparams (data) {
    // Parameter für FielDialog einlesen und an globales Array fileDialogParams senden
    fileDialogParams = {};
    if ("insert_str" in data) {
        fileDialogParams.insert_str = data.insert_str; 
    } else {
        fileDialogParams.insert_str = "explore";
    };
    if ("spath" in data) {
        fileDialogParams.spath = data.spath;
    };
    if ("ftype" in data) {
        fileDialogParams.ftype = data.ftype;
    };
    if ("updir" in data) {
        fileDialogParams.updir = data.updir;
    };
    //console.log ("getFDParams: ", JSON.stringify (fileDialogParams));
};


function fileExplore (par){
    // https://codeburst.io/explaining-value-vs-reference-in-javascript-647a975e12a0
    var jpar = JSON.stringify(par);
    // console.log ("fileExplore: " +jpar);
    var params = JSON.parse(jpar); //pure function
    var clickid, insert, dirinsert, tblinsert, dirid, tblid;
    // Insert-Punkte: #explore, #exploreDir, #exploreTable
    if ("insert_str" in params) {
        insert  = params.insert_str;
        
    } else {
        insert = "explore";
    };
    clickid = '#' + insert;
    dirinsert = insert + "Dir";
    tblinsert = insert + "Table";
    dirid     = '#' + dirinsert;
    tblid     = '#' + tblinsert; 

    var insertpoint = "<div class='alert alert-info text-break' "
                      + "id='" + dirinsert + "'></div>"
                      + "<div id='" + tblinsert + "'></div>";

    $(clickid).html (insertpoint);
    $.get ("/explore/"+jpar, function (data){
        var jresult, basedir, updirectory;
        jresult = JSON.parse(data);
        // updir:
        if (jresult.updir == undefined) {
            jresult.updir = fileDialogParams.updir;
        };
        // basedir:
        basedir = jresult.basedir.replace(/\\/g,'+'); // Windows
        basedir = basedir.replace(/\//g,'+'); // Linux
        fileDialogParams.filepath = basedir;
        // Anzeige für basedir kürzen 
        // (Chrome und Safari verweigern den Zeilenumbruch)
        //var viewdir = jresult.basedir.replace(/\\/g,' '); // Windows
        //viewdir     = viewdir.replace(/\//g,'+'); // Linux

        // nur beim ersten Aufruf von explore:
        if (fileDialogParams.basedir == undefined) {
            fileDialogParams.basedir  = basedir;
        };
        
        //$("#exploreDir").html   (viewdir);
        $(dirid).html (jresult.basedir);
        $(tblid).html (jresult.table);

        $(".dir").on ("click", function(){
            var spath = $(this).text();
            params.spath = spath;
            params.basedir = basedir;
            if (spath == "..") {
                // https://stackoverflow.com/questions/651563/getting-the-last-element-of-a-split-string-array
                var last, len;
                last = basedir.split(/[+ ]+/).pop(); // letztes Pfadelement
                len = basedir.length - (last.length + 1); // '+' mitzählen
                updirectory = basedir.substring (0, len);
                //console.log ("compare: "+ updirectory);
                if (updirectory == fileDialogParams.basedir){
                    params.updir = fileDialogParams.updir;
                } else {
                    params.updir = 'true';    

                };
            } else {
                params.updir = 'true'; 
            };
            fileExplore (params);
        });

        $(".file").on ("click", function(){
            var spath = $(this).text();
            $("#filename").attr ("value",spath);
            fileDialogParams.result = spath;
            activateFileSelector ();
            //console.log ("datei:"+ $("#filename").attr("value"));
        });
    });

}  // ende explore

// activateFileSelector() wird zur Anzeige des ausgewählten Files verwendet.
// kann für explore umdefiniert werden:
function activateFileSelector () {}

// --- Buttons für CSV-Tabellen ----------------------------------------------


function activateUploadCsv (insert_id) {
    // 'Upload' Button
    $(".uploadButton").on ("click", function (event) {
            
        // CSV-Datei:
        //var tableElem = $("#csvtable");
        var filePath = $("#csvtable").attr("pluspath");
        // links: Eingabeformular, rechts: Tabelle (wie bei newline)

        var callstr = "/uploadcsv/" + filePath;
        $.get (callstr, function (data){
            var pdata = JSON.parse(data);
            $(insert_id).html (pdata);
            
            // Input-Felder aktivieren:
            $('.custom-file-input').on('change', function() { 
                let fileName = $(this).val().split('\\').pop(); 
                //console.log ("FileName: "+ fileName);
                $(this).next('.custom-file-label')
                    .addClass("selected")
                    .html(fileName); 
            });

            // Buttons aktivieren:
            $("#closeButton").on ("click", function (event){
                location.reload ();
            });
        }); // ende $get uploadcsv
    });
};

// --- Room Upload --------------------------------------------------------
function activateUploadRoom (insert_id) {
    // 'Upload' Button
    $(".roomUpload").on ("click", function (event) {
            
        $.get ("/uploadroom", function (data){
            var pdata = JSON.parse(data);
            $(insert_id).html (pdata);
            
            // Input-Felder aktivieren:
            $('.custom-file-input').on('change', function() { 
                let fileName = $(this).val().split('\\').pop(); 
                //console.log ("FileName: "+ fileName);
                $(this).next('.custom-file-label')
                    .addClass("selected")
                    .html(fileName); 
            });

            // Buttons aktivieren:
            $("#closeButton").on ("click", function (event){
                location.reload ();
            });
        }); // ende $get uploadcsv
    });
};

