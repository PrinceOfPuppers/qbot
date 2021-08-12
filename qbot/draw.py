
'''
┌───┐
│ H │
└───┘
'''
top = "┌───┐"
mid = "│   ‎│" # contains U+2002, so ncurses overlay does not draw rail through it
bottom = "└───┘"

oneQubitMeasurement = "◁ "
controlSymbol = "●"
vertLine = "│"
horizontalLine = "─"

circuitLeftMargin = 3

import curses

def drawGate( circuitWin, gateX: int, gatefirstRail: int, gateNumRails: int, gateSymbol: int, gateControls:[int]):
    '''
    circuitDiagramCorner is the top left hand corner of the circuit diagram 
    '''
    leftOfGate = gateX + circuitLeftMargin -2
    centerGate = leftOfGate + 2

    firstRail = gatefirstRail*3 + 1
    topOfGate = firstRail - 1

    circuitWin.addstr(topOfGate, leftOfGate, top)
    circuitWin.addstr(topOfGate+1, leftOfGate, mid)

    for i in range(0,gateNumRails-1):
        for j in range(0,3):
            circuitWin.addstr(topOfGate + i*3 + j + 2, leftOfGate, mid)
    
    bottomOfGate = topOfGate + 3*(gateNumRails-1) + 2 
    circuitWin.addstr(bottomOfGate, leftOfGate, bottom)
    
    # add gate symbol
    circuitWin.addch((topOfGate -1 + (3*gateNumRails + 1)//2), centerGate, gateSymbol)

    # add controls
    gateControls.sort()
    prevPos = bottomOfGate
    for i, controlRail in enumerate(gateControls):
        pos = controlRail*3 + 1

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
        'width',
        'height',
        'numRails',
        'placedGatesWin',
        'toPlaceGateWin',
        'railsWin',
    )
    def __init__(self,y,x,numRails,width):
        height =  numRails*3 + 2
        self.numRails = numRails

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.placedGatesWin = curses.newwin(height, width, y, x)
        self.toPlaceGateWin = curses.newwin(height, width, y, x)
        self.railsWin = curses.newwin(height, width, y, x)
    
    def refreshAll(self):
        self.toPlaceGateWin.overlay(self.railsWin)
        self.placedGatesWin.overlay(self.railsWin)
        self.toPlaceGateWin.refresh()
        self.placedGatesWin.refresh()
        self.railsWin.refresh()
    
    def refreshRails(self):
        self.railsWin.refresh()
    
    def refreshPlacedGates(self):
        self.placedGatesWin.overlay(self.railsWin)
        self.placedGatesWin.refresh()
        self.railsWin.refresh()

    def refreshToPlaceGate(self):
        self.toPlaceGateWin.overlay(self.railsWin)
        self.toPlaceGateWin.refresh()
        self.railsWin.refresh()

    def drawRails( self ):
        rail = self.width*horizontalLine
        for railNum in range(0, self.numRails):
            railY = 3*railNum + 1
            self.railsWin.addstr(railY, 0, rail)


def main(stdscr):
    curses.use_default_colors()
    curses.can_change_color() == False
    # curses.init_pair(1, curses.COLOR_WHITE, -1)
    numRails = 5
    stdscr = curses.initscr()
    x =  1
    y = 0
    width = 30
    circuitBox = CircuitBox(y,x,numRails,width)
    from time import sleep

    circuitBox.drawRails()
    drawGate(circuitBox.placedGatesWin,0,1,1,'H',[0,2,3])
    circuitBox.refreshPlacedGates()
    sleep(1)
    drawGate(circuitBox.toPlaceGateWin,5, 2, 1, 'X',[0] )
    circuitBox.refreshToPlaceGate()
    # drawGate(scr,(0,0),0,1,1,'H',[])
    stdscr.getch()
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)