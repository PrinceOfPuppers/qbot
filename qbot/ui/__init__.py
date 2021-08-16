from qbot.ui.circuitBox import CircuitBox, drawGate, drawSwap
import curses
from time import sleep

def main(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    curses.use_default_colors()
    curses.nocbreak()
    numRails = 5
    stdscr = curses.initscr()
    x =  0
    y = 1
    width = 30
    circuitBox = CircuitBox(y,x,numRails,width,4)

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
        circuitBox.xOffset = i
        circuitBox.yOffset = i
        circuitBox.refresh(stdscr)

    stdscr.getch()
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)