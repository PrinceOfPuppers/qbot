import curses
import curses.panel

seperator = '═'

class StatusBar:
    __slots__ = (
        'width',
        # data being displayed
        'mode',
        'x',
        'xLabel',
        'topRightText',
    )

    def __init__(self, stdscr, startingMode = '--Mode--', topRightText = 'help: h '):
        self.xLabel = ' t='
        self.x = 0
        self.resize(stdscr)
        self.mode = startingMode
        self.topRightText = topRightText

    def resize(self,stdscr):
        _, self.width = stdscr.getmaxyx()
    
    def refresh(self,stdscr):
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
