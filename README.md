# clubdmx_code

LIGHT OPERATION with a Web interface, suitable for various DMX hardware and ethernet protocols.
For a demo visit <https://guntherseiser.pythonanywhere.com>. You'll need to login for playing with ClubDMX. I have prepared two users with different rights, details follow below.

(The Web page language is German. Contributers that translate to other languages are highly welcome.)

## Features

### Web Interface

ClubDMX runs on a Raspberry PI (or on any other computer with Linux OS) and delivers a website for the user interaction. In other words, the Raspberry PI hosts the software, the user operates on his favorite device, which can be a laptop, tablet or a smartphone. On this device no app is needed, a browser is sufficient.

The website is written in Responsive Design and adopts to the size of the screen.

### Open Lighting Architecture

The DMX connection is carried out by [OLA](https://www.openlighting.org/) . There is a lot of hardware options available, for example Enttec DMX USB Pro and DMX King. OLA establishes various ethernet protocols like ArtNet, sACN and others. An overview of the wide range of possibilities for DMX output is here:
<https://www.openlighting.org/ola/> .

### Scenes/Cues

The first and basic goal in the development of ClubDMX was to enable an easy handling of **Light Scenes (= Cues)**. 

ClubDMX offers various possibilities for **Cues**:
* Cues with Fader
* Cues with Button
* One Cue with top priority for direct handling the the hardware devices and creating new Cues
* Cuelists as collections of Cues, with fade-times and wait-times.

### Data stored in CSV files

All program data is stored in CSV files. This is a plain text format, that is highly compatible with most text editors and operating systems. Of course creating end editing is done in ClubDMX.

### Adapted to various Users

There is a login on the website, and then all user specific possibilities and data is activated. There are differnt roles of Users with different rights. Only after login you can you can operate DMX hardware.

### MIDI

In addition to the website ClubDMX can be operated by MIDI. For example with a KORG nanoKontrol-2. The buttons and faders of the NanoKontrol can be linked to the buttons and faders of ClubDMX.

Up to four MIDI inputs and for MIDI outputs can be connected to ClubDMX.

### OSC Input

[OSC](https://en.wikipedia.org/wiki/Open_Sound_Control) can link external software with ClubDMX. With it all devices with all attributes can be operated, as well as faders, buttons and cuelists defined in ClubDMX.

This feature is extensively tested with [Isadora](https://troikatronix.com/). 
For interaction between ClubDMX and Isadora there are example Isadora patches and user actors available.

## Play with the demo

There is a demo of ClubDMX on [pythonanywhere.com](https://guntherseiser.pythonanywhere.com/index). Without login you can view some pictures of ClubDMX in action and read the documentation. It's a good starting point to get some ideas what to do with ClubDMX. 

I suggest that you login as user *basic* next. This gives you the opportunity to use ClubDMX as intended and prepared by a *standard* or *admin* user. 

After playing as user *basic* a while go ahead an log in as user "Standard". Now you get the opportunity to set up a room, a certain show or whatever environment you plan.

User *basic* has the password *basic*

User *Standard* has the password *Standard2021*

## Getting started with real hardware

Please have a look at the [software install instructions](install.md). You will find detailed install instructions for setting up a Raspberry PI from scratch. A PI-4 is recommended. 

If you plan to test and work with older hardware like unused laptops or so, this is also fine. I can recommend to install Debian with a lightweight desktop like LXDE or LXQT. The install file mentioned above contains instructions for Debian machines also.

Also fine and tested is to use a VirtualBox on a Windows host to install a Debian client and ClubDMX. 

## License

[MIT](LICENSE.md)