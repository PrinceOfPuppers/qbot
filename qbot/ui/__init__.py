from qbot.ui.circuitBox import CircuitBox, drawGate, drawSwap
from qbot.ui.statusBar import StatusBar
from qbot.ui.selectedBox import SelectedBox
import curses
from time import sleep

def setupUI(stdscr, numRails):
    selectedBoxHeight = 4
    nonCircuitBoxHeight = selectedBoxHeight + 2

    stdscr.clear()
    curses.curs_set(0)
    curses.use_default_colors()
    curses.nocbreak()

    statusBar = StatusBar(stdscr)
    statusBar.refresh(stdscr)
    selectedBox = SelectedBox(stdscr, selectedBoxHeight)

    selectedBox.refresh(stdscr)

def main(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    curses.use_default_colors()
    curses.nocbreak()

    statusBar = StatusBar(stdscr)
    statusBar.refresh(stdscr)

    selectedBox = SelectedBox(stdscr, 4)
    selectedBox.text = "this is a test of the selected box to see how well it works, im writing somthing really long to see how it splits textttttttttt aaaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb vcvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv this is a test of the selected box to see how well it works, im writing somthing really long to see how it splits textttttttttt aaaaaaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb vcvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv aa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa bb"
    selectedBox.refresh(stdscr)

    numRails = 6
    stdscr = curses.initscr()
    x = 0 
    y = 2
    width = 30
    circuitBox = CircuitBox(stdscr, y, x, numRails, width, 5)

    circuitBox.drawRails()
    drawGate(circuitBox.placedGatesWin,0,1,1,'∡ ±',[0,2,3])
    drawGate(circuitBox.placedGatesWin,1,1,1,'H',[0,3])
    drawGate(circuitBox.toPlaceGateWin,2, 1, 1, 'X',[0] )
    circuitBox.refresh(stdscr)
    circuitBox.refresh(stdscr)
    stdscr.getch()
    drawGate(circuitBox.toPlaceGateWin,0, 1, 2, 'X',[0] )
    circuitBox.refresh(stdscr)
    stdscr.getch()
    circuitBox.placedGatesWin.clear()
    circuitBox.refresh(stdscr)
    stdscr.getch()
    drawSwap(circuitBox.placedGatesWin, 3, 0, 2)
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