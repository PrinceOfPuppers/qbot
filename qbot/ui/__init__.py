from qbot.ui.circuitBox import CircuitBox, drawGate, drawSwap
import curses
from time import sleep

def main(stdscr):
    stdscr.clear()
    curses.use_default_colors()
    curses.nocbreak()
    numRails = 5
    stdscr = curses.initscr()
    x =  3
    y = 3
    width = 30
    circuitBox = CircuitBox(y,x,numRails,width)
    circuitBox.resizeBox(25,90)

    circuitBox.drawRails()
    drawGate(circuitBox.placedGatesWin,0,1,1,'∡ ±',[0,2,3])
    drawGate(circuitBox.placedGatesWin,1,1,1,'H',[0,3])
    drawGate(circuitBox.toPlaceGateWin,2, 1, 1, 'X',[0] )
    circuitBox.refresh()
    circuitBox.refresh()
    stdscr.getch()
    drawGate(circuitBox.toPlaceGateWin,0, 1, 2, 'X',[0] )
    circuitBox.refresh()
    stdscr.getch()
    circuitBox.placedGatesWin.clear()
    circuitBox.refresh()
    stdscr.getch()
    drawSwap(circuitBox.placedGatesWin, 3, 0, 2)
    circuitBox.refresh()
    stdscr.getch()
    for i in range(0,100):
        sleep(0.1)
        circuitBox.xOffset = i
        circuitBox.yOffset = i
        circuitBox.refresh()

    stdscr.getch()
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)