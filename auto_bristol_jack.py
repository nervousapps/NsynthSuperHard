import os
import time
import jack
import mido
import smbus
import struct
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from gpiozero import Button

# Midi
def connect_midi_ports():
    mido.open_output()
    print(mido.get_output_names())
    inport = mido.open_input(mido.get_output_names()[0])
    outport = mido.open_output(mido.get_output_names()[3])
    return inport, outport

# Get the list of available synths
available_synths = []


# Init jack client
client = jack.Client('MyGreatClient')

synthname = "mini"

button1 = Button(5)
button2 = Button(6)
button3 = Button(13)
button4 = Button(26)

bus = smbus.SMBus(1)

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)
 
# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 5
 
# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3D, reset=oled_reset)

def screen(text):
    # Clear display.
    oled.fill(0)
    oled.show()
     
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))
     
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
     
    # Draw a white background
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
     
    # Draw a smaller inner rectangle
    draw.rectangle(
        (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
        outline=0,
        fill=0,
    )
     
    # Load default font.
    font = ImageFont.load_default()
     
    # Draw Some Text
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )
     
    # Display image
    oled.image(image)
    oled.show()


def test_checksum(data):
    uints = struct.unpack('4I', data)
    chk = 0xaa55aa55
    chk += uints[0]
    chk += uints[1]
    chk += uints[2]
    return (chk & 0xffffffff) == uints[3]


def check_inputs():
    address = 0x47

    try:
        data = bus.read_i2c_block_data(address, 0, 16)
    except IOError:
        print('did not respond')
        time.sleep(1)
#     print([bytes(chr(d), 'utf-8') for d in data])
#     data = b"".join([bytes(chr(d), 'utf-8') for d in data]) #map(chr, data))
#     unpacked = struct.unpack('2b4b6BI', data)
#     touch = unpacked[:2]
#     rots = unpacked[2:6]
#     pots = unpacked[6:12]
#     chk = unpacked[12]
#     print('touch={} rots={} pots={} chk=0x{:08x} {}'.format(
#         touch, rots, pots, chk,
#         'passed' if test_checksum(data) else 'failed',
#     ))
    time.sleep(0.1)
    pressed = False
    if button1.is_pressed:
      print("Pressed")
      pressed = True
    if button2.is_pressed:
      print("Pressed")
      pressed = True
    if button3.is_pressed:
      print("Pressed")
      pressed = True
    if button4.is_pressed:
      print("Pressed")
      pressed = True
    return data, pressed

try:
    screen("NsynthSuperHard")
    previous_inputs_data, pressed = [], False
    inport, outport = None, None
    with client:
        while True:
            inputs_data, pressed = check_inputs()
            if inputs_data != previous_inputs_data:
                print(previous_inputs_data)
                previous_inputs_data = inputs_data
                print(previous_inputs_data)
                synthname = "juno"
            if pressed:
                try:
                    inport.close()
                    outport.close()
                except:
                    pass
                screen(synthname)
                result = os.popen("startBristol -exit &")
                time.sleep(5)
                result = os.popen(f"startBristol -{synthname} -jack -midi alsa &")
                time.sleep(5)
                # When entering this with-statement, client.activate() is called.
                # This tells the JACK server that we are ready to roll.
                # Our process() callback will start running now.

                # Connect the ports.  You can't do this before the client is activated,
                # because we can't make connections to clients that aren't running.
                # Note the confusing (but necessary) orientation of the driver backend
                # ports: playback ports are "input" to the backend, and capture ports
                # are "output" from it.
                available_ports = client.get_ports()
                if not available_ports:
                    raise RuntimeError('No available_ports')
                print(available_ports)
                print(f"Connect {available_ports[2]} to {available_ports[0]}")
                client.connect(available_ports[2], available_ports[0])
                client.connect(available_ports[3], available_ports[1])

                inport, outport = connect_midi_ports()
                synthname = "mini"
            if inport and outport:
                msg = inport.poll()
                if msg and not "aftertouch" in msg.type:
                    print(msg)
                    outport.send(msg)
except KeyboardInterrupt:
    result = os.popen("startBristol -exit &")



