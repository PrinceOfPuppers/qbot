import curses
import curses.panel

top = "┌───┐"
mid = "│   ‎│" # contains U+2002, so ncurses overlay does not draw rail through it
bottom = "└───┘"

oneQubitMeasurement = "◁ "
controlSymbol = "●"
vertLine = "│"
horizontalLine = "─"

circuitLeftMargin = 3

# Ensures Space Between Gates
xToColFactor = 3


def railToY(railNum):
    return railNum*3 + 2

def drawGate( circuitWin, gateX: int, gateFirstRail: int, gateNumRails: int, gateSymbol: int, gateControls:[int]):
    '''
    circuitDiagramCorner is the top left hand corner of the circuit diagram 
    '''
    leftOfGate = xToColFactor*gateX + circuitLeftMargin -2
    centerGate = leftOfGate + 2

    firstRail = railToY(gateFirstRail)
    topOfGate = firstRail - 1

    circuitWin.addstr(topOfGate, leftOfGate, top)
    circuitWin.addstr(topOfGate+1, leftOfGate, mid)

    for i in range(0,gateNumRails-1):
        for j in range(0,3):
            circuitWin.addstr(railToY(i + gateFirstRail) + j + 1, leftOfGate, mid)
    
    bottomOfGate = railToY(gateNumRails + gateFirstRail-1) + 1 
    circuitWin.addstr(bottomOfGate, leftOfGate, bottom)
    
    # add gate symbol
    circuitWin.addch((topOfGate + (3*gateNumRails - 1)//2), centerGate, gateSymbol)

    # add controls
    gateControls.sort()
    prevPos = bottomOfGate
    for i, controlRail in enumerate(gateControls):
        pos = railToY(controlRail)

        # remember, down is larger
        if pos > bottomOfGate:
            for y in range(prevPos+1, pos):
                circuitWin.addch(y, centerGate, vertLine)
            
            circuitWin.addch(pos, centerGate, controlSymbol)
            prevPos = pos
            continue

        circuitWin.addch(pos, centerGate, controlSymbol)
        for y in range(pos+1,topOfGate):
            circuitWin.addch(y, centerGate, vertLine)

class CircuitBox:
    __slots__ = (
        'x',
        'y',
        'xOffset',
        'yOffset',
        'width',
        'height',
        'numRails',
        'placedGatesWin',
        'toPlaceGateWin',
        'railsWin',
        'box',
        '_rail',
        '_xNums'
    )
    def __init__(self,y,x,numRails, maxHeight,width):
        height =  numRails*3 + 2
        self.numRails = numRails

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if height > maxHeight:
            self.height = maxHeight

        self.xOffset = 0
        self.yOffset = 0

        self.placedGatesWin = curses.newwin(height, width, y, x)
        self.toPlaceGateWin = curses.newwin(height, width, y, x)
        self.railsWin = curses.newwin(height, width, y, x)
        self.box = curses.newpad(height, width)


        self._rail = self.width*horizontalLine
        self._xNums = [circuitLeftMargin*" "+"0"]

        for i in range(1,(self.width)//xToColFactor - xToColFactor):
            self._xNums.append(str(i))
        self._xNums = (xToColFactor*" ").join(self._xNums)
    
    def refresh(self):

        if self.yOffset > self.height:
            self.yOffset = self.height
        if self.xOffset > self.width:
            self.xOffset = self.width

        self.box.clear()
        self.box.noutrefresh(self.y, self.x, self.yOffset, self.xOffset, self.height, self.width)
        self.railsWin.overlay(self.box)
        self.placedGatesWin.overlay(self.box)
        self.toPlaceGateWin.overlay(self.box)
        self.box.refresh(self.y, self.x, self.y, self.x, self.height, self.width)

    def drawRails( self ):
        self.railsWin.addstr(0,0,self._xNums)

        for railNum in range(0, self.numRails):
            railY = railToY(railNum)
            self.railsWin.addstr(railY, 0, self._rail)


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
    from time import sleep

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