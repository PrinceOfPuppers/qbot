from qbot.ui.circuitBox import CircuitBox, drawGate, drawSwap
import curses
from time import sleep

def main(stdscr):
    curses.use_default_colors()
    curses.can_change_color() == False
    # curses.init_pair(1, curses.COLOR_WHITE, -1)
    numRails = 5
    maxHeight = 20
    stdscr = curses.initscr()
    x =  3
    y = 3
    width = 40
    circuitBox = CircuitBox(y,x,numRails,maxHeight,width)

    circuitBox.drawRails()
    drawGate(circuitBox.placedGatesWin,0,1,1,'H',[0,2,3])
    drawGate(circuitBox.placedGatesWin,2,1,2,'H',[0,3])
    circuitBox.refresh()
    sleep(1)
    drawGate(circuitBox.toPlaceGateWin,0, 1, 2, 'X',[0] )
    circuitBox.refresh()
    sleep(1)
    circuitBox.placedGatesWin.clear()
    circuitBox.refresh()
    sleep(1)
    drawSwap(circuitBox.placedGatesWin, 3, 0, 3)
    circuitBox.refresh()
    sleep(1)
    for i in range(0,21):
        sleep(0.1)
        circuitBox.xOffset = i
        circuitBox.yOffset = i
        circuitBox.refresh()
    circuitBox.toPlaceGateWin.clear()

    # circuitBox.railsWin.touchwin()

    stdscr.getch()
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)