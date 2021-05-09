setup_audio() {
    if grep -q '^dtparam=audio=on' /boot/config.txt
    then
        echo 'Disabling on board audio'
        sed -i -e 's/dtparam=audio=on/#dtparam=audio=on/' /boot/config.txt
    fi

    if ! grep -q "^dtoverlay=iqaudio-dac" /boot/config.txt
    then
        echo 'Enabling I2S + I2C audio'
        printf "\n# Enable I2S + I2C audio\ndtoverlay=iqaudio-dac\n" >> /boot/config.txt
    fi
}


setup_i2c() {
    if grep -q '^#dtparam=i2c_arm=on' /boot/config.txt
    then
        echo 'Enabling I2C'
        sed -i -e 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/' /boot/config.txt
    fi

    if ! grep -q '^dtparam=i2c_arm_baudrate=640000' /boot/config.txt
    then
        echo 'Setting I2C to high speed'
        printf "\n# Set I2C to high speed\ndtparam=i2c_arm_baudrate=640000\n" >> /boot/config.txt
    fi

    if ! grep -q '^i2c-dev' /etc/modules
    then
        echo 'Enabling i2c-dev module'
        printf "i2c-dev\n" >> /etc/modules
    fi
}


setup_serial() {
    if grep -q 'console=serial' /boot/cmdline.txt
    then
        echo 'Disabling console serial'
        sed -i -e 's/console=serial[^ ]* //' /boot/cmdline.txt
    fi

    if ! grep -q '^dtoverlay=pi3-miniuart-bt' /boot/config.txt
    then
        echo 'Enabling serial MIDI'
        printf "\n# Enable seiral MIDI\nenable_uart=1\ndtoverlay=pi3-miniuart-bt\ndtoverlay=midi-uart0\n" >> /boot/config.txt
    fi
}

install_all_deps() {
  sudo apt-get update
  sudo apt-get upgrade -y
  sudo apt-get -y bristol

  sudo apt update
  sudo apt upgrade -y
  sudo apt install -y python3-mido python3-smbus python3-gpiozero

  python3 -m pip install setuptools JACK-Client adafruit-circuitpython-ssd1306 python-rtmidi
}

install_all_deps
setup_i2c
setup_audio
setup_serial
