#!/home/pi/py/bin/python
"""
    Flashing Station GUI uses PySimpleGUI with PySide2 Bindings to
    create a quick and simple interface to flashing certain microcontrollers
    with specific hex files.

    Dependencies:
    1) native linux 
    2) avrdude v 6.3.20190619
    3) AVR Pocket Programmer by SparkFun
    4) PySide2

"""
import sys
sys.path.insert(0, 'src/')

from wtfs import WTFS

if __name__ == "__main__":
    WTFS().run()
