import PySimpleGUI as sg
import glob
import sys
import subprocess
from multiprocessing import Process
from typing import *

MAX_HEIGHT = 400
MAX_WIDTH = 300


class WTFS:
    def __init__(self):
        self.window = None
        self.boards = dict()
        self.cur_board = dict()
        self.layout = self.__init_layout()

        # get path to avrdude - must be installed
        self.avrdude_path = subprocess.check_output(['which', 'avrdude'
                                                     ]).decode().strip()

    def run(self) -> None:

        layout = [[sg.Text('Some text on Row 1')],
                  [sg.Text('Enter something on Row 2'),
                   sg.InputText()], [sg.Button('Ok'),
                                     sg.Exit()]]

        self.window = sg.Window("WT Flashing Station",
                                self.layout,
                                size=(MAX_HEIGHT, MAX_WIDTH))

        while True:
            event, values = self.window.read()
            if event in (None, "Exit"):
                break

            if "board_selection" == event:
                selected_board = values[event]
                hex_files = glob.glob(f"hex/{selected_board}*.hex")
                eeprom_files = glob.glob(f"eeprom/{selected_board}*.hex")

                if len(eeprom_files) == 0:
                    sg.Popup(
                        f"WARNING: EEPROM Hex File not found for {selected_board}."
                    )

                if len(hex_files) == 0:
                    sg.PopupError(
                        f"Hex File not found for {selected_board} check to see if board exists in .boards file"
                    )
                    continue

                if len(hex_files) > 1 or len(eeprom_files) > 1:
                    sg.PopupError("Multiple hex files OR eeprom files found.")
                    sys.exit(-1)

                else:
                    hex_file_path = hex_files[0]
                    try:
                        eeprom = eeprom_files[0]
                    except IndexError:
                        eeprom = None

                    fw_version = hex_file_path[5 + len(selected_board):-4]
                    self.window["fw_version"](f"FW: {fw_version}")
                    prgmr = "usbtiny"
                    uC = self.boards[selected_board]
                    conf = "avrdude.conf"

                    self.cur_board = {
                        'path': hex_file_path,
                        'programmer': prgmr,
                        'board': uC,
                        'conf': conf,
                        'eeprom': eeprom
                    }
                    print(self.cur_board)

            if 'detect_btn' in event:
                if len(self.cur_board) == 0:
                    sg.PopupError("Board not selected")
                    continue

                _, output = subprocess.Popen(
                    [
                        'sudo', self.avrdude_path,
                        f"-C{self.cur_board['conf']}",
                        f"-c{self.cur_board['programmer']}",
                        f"-p{self.cur_board['board']}"
                    ],
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE).communicate()

                sg.PopupOK(output.decode(), keep_on_top=True, title="Result")

            if 'flash_btn' in event:
                if len(self.cur_board) == 0:
                    sg.PopupError("Board not selected")
                    continue

                    # Flash EEPROM
                    if self.cur_board['eeprom'] is not None:
                        sg.PopupQuickMessage("Flashing EEPROM...")
                        _, output = subprocess.Popen(
                            [
                                'sudo',
                                self.avrdude_path,
                                f"-C{self.cur_board['conf']}",
                                f"-c{self.cur_board['programmer']}",
                                f"-p{self.cur_board['board']}",
                                f"-Uflash:w:{self.cur_board['path']}:i",
                            ],
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE).communicate()

                    sg.PopupOK(output.decode(),
                               keep_on_top=True,
                               title="EEPROM Result")
                # Flash Program
                sg.PopupQuickMessage("Flashing Program Memory...")
                _, output = subprocess.Popen(
                    [
                        'sudo',
                        self.avrdude_path,
                        f"-C{self.cur_board['conf']}",
                        f"-c{self.cur_board['programmer']}",
                        f"-p{self.cur_board['board']}",
                        f"-Uflash:w:{self.cur_board['path']}:i",
                    ],
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE).communicate()

                sg.PopupOK(output.decode(),
                           keep_on_top=True,
                           title="Program Flash Result")
        self.window.close()

    def __init_layout(self) -> List:
        with open('.boards', 'r') as f:
            boards = [l.strip() for l in f.readlines()]
            for board in boards:
                b = board.split(',')
                b, uC = b[0], b[1]
                self.boards[b] = uC

        layout = [[sg.Text("Select Board")],
                  [
                      sg.DropDown(values=[b.split(',')[0] for b in boards],
                                  key="board_selection",
                                  enable_events=True)
                  ], [sg.Text("", size=(20, 1), key="fw_version")],
                  [
                      sg.Button("FLASH",
                                key="flash_btn",
                                size=(20, 4),
                                pad=(0, 30)),
                      sg.Button("DETECT",
                                key="detect_btn",
                                size=(20, 4),
                                pad=(5, 30))
                  ]]
        return layout
