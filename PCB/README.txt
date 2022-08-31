(see parent README.md)

# Requirements

Made with KiCad 6


## KiCad Plugins

https://github.com/bouni/kicad-jlcpcb-tools


# Track changes

[cadlab.io](https://cadlab.io/project/25849/)


# Specifications

(see parent README.md)


# Fabrication

The PCB is intended to be manufactured by JLCPCB so the outputs meet they requirements. Necessary files for manufacturing and assembly are in the jlcpcb folder


# BOM

LCSC parts are inside PCB\jlcpcb\assembly (to be assembly by jlcpcb or sourced from there and solder them manually)
- 12x Kailh choc Low profile Mechanical Switch, https://a.aliexpress.com/_uHRL47  (10 or 70)
- 12x Keycaps for Kailh choc, https://a.aliexpress.com/_uGXK51 (transparent-choc)
- 1x SSD1306 38x12mm OLED Display, https://a.aliexpress.com/_vNfBEr
- 1x RaspberryPi Pico, https://www.raspberrypi.com/products/raspberry-pi-pico/

# TODO

- Cover vias with soldermask
- Add diodes or limit resistors to keyboard matrix
- Power planes for 3.3v and 5v
- all pots (R1, R2, R3) swap GND and 3,3
