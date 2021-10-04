# NsynthSuperHard
Use the OpenNsynthSuper hardware to run other synths.

Jack used for audio and midi driver.

# Available synths
  - FluidSynth (https://www.fluidsynth.org/)
  - Bristol (http://bristol.sourceforge.net/)

# Prerequisites
The OpenNsynthSuper firmware need to be already flashed in the microcontroller.

If not, please follow the instructions here https://github.com/googlecreativelab/open-nsynth-super/tree/master/firmware or here https://github.com/googlecreativelab/open-nsynth-super#3-prepare-the-sd-card.
Just follow the instructions 3 and 4 for the second option, get the 16GB image to go faster.

If the OpenNsynthSuper was up and running then the firmware is already loaded, no need to install it.

# Setup
The Raspberry need access to internet, activate the wlan or plug in an ethernet cable.
  - Prepare a SD card with Raspbian (Desktop or Lite, lite recommended) (don't forget to add ssh named file in boot partition in order to enable ssh at boot).
  See https://www.raspberrypi.org/software/
  - Boot the Raspberry with the SD card previously prepared inserted
  - Clone this repo
  - Run : bash setup_install_all.sh

# Links
https://www.raspberrypi-spy.co.uk/2018/04/i2c-oled-display-module-with-raspberry-pi/
https://github.com/googlecreativelab/open-nsynth-super
