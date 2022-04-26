import curses
import curses.panel

class TextPanel:
    __slots__ = (
        'name',
        'contents',
        'x',
        'y',
        'width',
        'height',
    )

    def __init__(self, stdscr, startingMode = '--Mode--', topRightText = 'help: h '):

        self.infoWin = curses.newwin(height, width, y, x)
        self.infoPanel = curses.panel.new_panel(self.infoWin)

        self.xLabel = ' t='
        self.x = 0
        self.resize(stdscr)
        self.mode = startingMode
        self.topRightText = topRightText

    def _getSize(self, stdscr):
        sy, sx = stdscr.getmaxyx()
        my, mx = int(sy/2), int(sx/2)
        self.width = sx*widthScaler
        self.height = 

    def resize(self,stdscr):

        widthScaler = 0.6

        self.infoPanel.resize()
        self.infoWin.move

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
