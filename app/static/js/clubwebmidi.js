/* CLUBWEBMIDI */

// Webmidi Zuordnungen treffen:
function showDeviceInfo (device, index) {
  console.log (index + ": " + device.name);
}

function onWebmidiEnabled() {
  if (WebMidi.inputs.length < 1) {
    console.log ("No device detected.");
    // document.body.innerHTML+= "No device detected.";
  } else {
    WebMidi.inputs.forEach (showDeviceInfo);

    // WebMidi.inputs.forEach((device, index) => {
    //   document.body.innerHTML+= `${index}: ${device.name} <br>`;
    // });

    const mySynth = WebMidi.inputs[0];
    mySynth.addListener ("controlchange", webmidiListener);
    // const mySynth = WebMidi.getInputByName("TYPE NAME HERE!")

    // mySynth.channels[1].addListener("controlchange", e => {
    //   document.body.innerHTML+= `${mySynth.name}
    //       ${e.controller.number} ${e.value} <br>`;
    // });

  }
}

function webmidiListener (event) {
  // Auswertung des Midi-Events
  let sliderval = event.value * 255;
  if (event.controller.number == "2") {
    // console.log ("controller 3 - value: " + event.value);
    $.post ("/sliderlevel/0", {level:sliderval} );
  }
}


$(document).ready (function() {

  // Aktiviere Webmidi:
  WebMidi
  .enable ()
  .then (onWebmidiEnabled)
  .catch (err => alert(err));  

});  