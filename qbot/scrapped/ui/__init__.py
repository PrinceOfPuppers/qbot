from qbot.ui.circuitBox import CircuitBox, drawGate, drawSwap
from qbot.ui.statusBar import StatusBar
from qbot.ui.selectedBox import SelectedBox
from qbot.ui.infoPanel import InfoPanel
import curses
from time import sleep
from enum import Enum


# modes

# normal: press i for info, g to place a gate, r to run, hjkl pan around

# help: help popup is open

# running: cirucit is running, n to step forward, s to enter select mode, escape to cancel running and return to normal

# select: select rails with jk and enter, selected rails are measured as one system at current point in circuit and output is put in selection box
#         press escape to return to running

# gate: popup opens with all gates, select one with hjkl and enter, afterwards enteres place mode

# measure: popup opens with all measurements, select one with hjkl and enter, afterwards enters place mode

# place: move gate around with hjkl, press enter to place gate, then jk enter to place controls (or other end of swap), escape finishes (return to normal) 

class State:
    def __init__(self, circuitBox, statusBar, selectedBox):
        self.mode = 'normal'
        self.circuitBox = circuitBox
        self.selectedBox = selectedBox
        self.statusBar = statusBar





def controls(mode):
    pass

def setupUI(stdscr, numRails, width):
    selectedBoxHeight = 4
    nonCircuitBoxHeight = selectedBoxHeight + 1

    stdscr.clear()
    curses.curs_set(0)
    curses.use_default_colors()
    curses.nocbreak()

    statusBar = StatusBar(stdscr)
    statusBar.refresh(stdscr)
    selectedBox = SelectedBox(stdscr, selectedBoxHeight)

    selectedBox.refresh(stdscr)

    circuitBox = CircuitBox(stdscr,2,0,numRails,width,nonCircuitBoxHeight)

    return circuitBox, statusBar, selectedBox

def main(stdscr):
    circuitBox, statusBar, selectedBox = setupUI(stdscr, 6,30)

    drawGate(circuitBox.placedGatesWin,0,1,1,'∡ ±',[0,2,3])
    drawGate(circuitBox.placedGatesWin,1,1,1,'H',[0,3])
    drawGate(circuitBox.toPlaceGateWin,2, 1, 1, 'X',[0] )
    circuitBox.refresh(stdscr)
    circuitBox.refresh(stdscr)
    stdscr.getch()
    drawGate(circuitBox.toPlaceGateWin,0, 1, 2, 'X',[0] )
    circuitBox.refresh(stdscr)
    stdscr.getch()
    circuitBox.clear(stdscr)
    circuitBox.refresh(stdscr)
    stdscr.getch()
    drawSwap(circuitBox.placedGatesWin, 3, 0, 2)
    circuitBox.refresh(stdscr)
    stdscr.getch()
    circuitBox.deleteGate(3, 0, 3)
    circuitBox.refresh(stdscr)
    stdscr.getch()

    circuitBox.resizeCircuit(stdscr, 2, 20)
    circuitBox.refresh(stdscr)
    stdscr.getch()

    for i in range(0,100):
        sleep(0.01)
        circuitBox.xOffset = 2*i
        circuitBox.yOffset = i
        circuitBox.refresh(stdscr)

    stdscr.getch()
    curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)
