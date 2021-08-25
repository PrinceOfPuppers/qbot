import curses
import curses.panel

seperator = '═'

class SelectedBox:
    __slots__ = (
        'width',
        'height',
        'boxLabel',
    )

    def __init__(self, stdscr, height, boxLabel = ' Selected State: '):
        self.height = height
        self.resize(stdscr)

    def resize(self, stdscr):
        _, self.width = stdscr.getmaxyx()
    
    def refresh(self, stdscr):
        self.resize(stdscr)
        xStr = self.xLabel + str(self.x)

        totalSpaceSize = ( self.width - len(xStr) - len(self.mode) - len(self.topRightText) )
        firstSpaceSize = totalSpaceSize // 2
        # if totalSpaceSize is odd, put the single extra space after the mode label
        secondSpaceSize = firstSpaceSize + (totalSpaceSize%2 != 0)

        statusBar = xStr + firstSpaceSize*" " + self.mode + secondSpaceSize*" " + self.topRightText

        stdscr.addstr(0, 0, statusBar)
        stdscr.addstr(1,0, self.width*seperator)
        stdscr.refresh()
