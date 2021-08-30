import curses
import curses.panel

horizontalLine = "─"
spaces = "     "

# gate drawing
top = "┌───┐"
mid = "│   ‎│" # contains U+2002, so ncurses overlay does not draw rail through it
bottom = "└───┘"
 
controlSymbol = "●"
vertLine = "│"

# measurement drawing
oneQubitMeasurement = "◁ "

# swap drawing 
adjacentSwap = [
    "╲  ╱─",
    " ╲╱  ",
    " ╱╲  ",
    "╱  ╲─",
]

distantSwapStart = [
    "╲   ╱",
    " ╲ ╱ ",
    "  V  ",
]
distantSwapEnd = [
    "  Λ  ",
    " ╱ ╲ ",
    "╱   ╲",
]

swapCrossing = "┼" #"╫" 
swapVert = vertLine #"║"

circuitLeftMargin = 3

# Ensures Space Between Gates
xToColFactor = 5


def railToY(railNum):
    return railNum*3 + 2

def gateXToWinX(x):
    return xToColFactor*x + circuitLeftMargin - 2

def drawGate( circuitWin, gateX: int, gateFirstRail: int, gateNumRails: int, gateSymbol: str, gateControls:[int]):
    '''
    circuitDiagramCorner is the top left hand corner of the circuit diagram 
    '''
    # replace spaces with U+2002 to occlude rails
    gateSymbol = gateSymbol.replace(" "," ")

    leftOfGate = gateXToWinX(gateX)
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
    symbolLines = (len(gateSymbol) - 1) // 3 + 1
    firstSymbolLine = topOfGate + (3*gateNumRails - 1)//2 - (symbolLines-1) // 2
    for line in range(0,symbolLines):
        firstChar = line*3
        lenLine = len(gateSymbol[firstChar: firstChar + 3])
        for i,char in enumerate(gateSymbol[firstChar: firstChar + 3]):
            circuitWin.addch(firstSymbolLine + line, leftOfGate + i + 1 + (lenLine == 1),char)

    # circuitWin.addch((topOfGate + (3*gateNumRails - 1)//2), centerGate, gateSymbol)

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

# def drawMeasurement( circuitWin, mx: int, mFirstRail: int, mNumRails: int, mSymbol: str ):
#     leftOfM = xToColFactor*mx + circuitLeftMargin - 2
    
#     firstRail = railToY(mFirstRail)

#     if mNumRails == 1:
#         circuitWin.addstr(firstRail, leftOfM, oneQubitMeasurement + mSymbol)
    
#     elif mNumRails == 2:

# swap drawings
# 
# distant swap
# ──╲   ╱────
#    ╲ ╱
#     v 
# ────┼─────
#     │ 
#     │
# ────┼─────
#     ^
#    ╱ ╲
# ──╱   ╲───
# 
# adjacent swap
# ──╲  ╱────
#    ╲╱
#    ╱╲
# ──╱  ╲────

def drawSwap(circuitWin, swapX: int, swapFirstRail: int, swapSecondRail: int):
    if(swapFirstRail == swapSecondRail):
        return

    swapFirstRail = min(swapFirstRail,swapSecondRail)
    swapSecondRail = max(swapFirstRail,swapSecondRail)

    firstRail = railToY(swapFirstRail)

    leftOfSwap = gateXToWinX(swapX)

    if( (swapSecondRail - swapFirstRail) == 1 ):
        for i,s in enumerate(adjacentSwap):
            circuitWin.addstr(firstRail + i, leftOfSwap, s )
        return
 

    midSwap = leftOfSwap + len(distantSwapStart[0])//2

    for i,s in enumerate(distantSwapStart):
        circuitWin.addstr(firstRail + i, leftOfSwap, s)

    railUnderFirstY = railToY(swapFirstRail + 1)
    circuitWin.addstr(railUnderFirstY , midSwap, swapCrossing)

    y = railUnderFirstY + 1
    for _ in range(0, swapSecondRail - swapFirstRail - 2):
        circuitWin.addstr(y , midSwap, swapVert)
        circuitWin.addstr(y+1 , midSwap, swapVert)
        circuitWin.addstr(y+2 , midSwap, swapCrossing)
        y+=3
    
    for i,s in enumerate(distantSwapEnd):
        circuitWin.addstr(y + i, leftOfSwap, s)
    
    return
        

 
class CircuitBox:
    __slots__ = (
        'x',
        'y',
        'width',
        'height',
        'numRails',
        'gateWidths',
        'xOffset', # box variables
        'yOffset',
        'boxWidth',
        'boxHeight',
        'heightRemaining',
        'placedGatesWin',
        'toPlaceGateWin',
        'railsWin',
        'box',
        '_rail',
        '_xNumsList',
        '_xNums'
    )
    def __init__(self, stdscr, y, x, numRails, gateWidths, heightRemaining):
        '''
        heightRemaining is how much of the terminal should be left for other ui elements
        '''
        height = railToY(numRails)
        width = gateXToWinX(gateWidths) + circuitLeftMargin

        # size of the entire circuit in rails and gate widths
        # note that this is the size of placedGatesWin, toPlaceGateWin and railsWin
        self.numRails = numRails
        self.gateWidths = gateWidths

        # x and y coord of top left portion of cirucitBox on the screen
        self.x = x
        self.y = y
        # same as numRails and gateWidths except in rows and cols
        self.width = width
        self.height = height

        # x and y offset of self.box, used for scrolling the window
        self.xOffset = 0
        self.yOffset = 0

        # height of screen - height of circuit box 
        self.heightRemaining = heightRemaining

        self.placedGatesWin = curses.newwin(height, width, y, x)
        self.toPlaceGateWin = curses.newwin(height, width, y, x)
        self.railsWin = curses.newwin(height, width, y, x)

        # size of the box displayed on screen (note can be smaller than pad self.box, but not larger)
        self.boxHeight = 0
        self.boxWidth  = 0

        # a buffer of 2 is added to the width to prevent smearing
        self.box = curses.newpad(height+y, width + x + 2 )
        self._resizeBox(stdscr)

        self._createRailsStr()

        self._xNumsList = [circuitLeftMargin*" "+"0"]
        self._createTopNumsStr()

        self.drawRails()

    def _createTopNumsStr(self):
        currentLen = len(self._xNumsList)
        newLen = (self.width -  circuitLeftMargin)//(xToColFactor) + 1
        if newLen > currentLen:
            for i in range(currentLen,newLen):
                num = str(i)
                self._xNumsList.append((xToColFactor-len(num))*" " + num)

        self._xNums = "".join(self._xNumsList[0:newLen])

    def _createRailsStr(self):
        self._rail = self.width*horizontalLine

    def _resizeBox(self, stdscr):
        y,x = stdscr.getmaxyx()
        boxWidth  = x - 1
        boxHeight = y - self.heightRemaining - 1
        

        if boxWidth != self.boxWidth or boxHeight != self.boxHeight:
            self.boxWidth = min(self.width + self.x,boxWidth) 
            self.boxHeight = min(self.height + self.y,boxHeight)
        
        oldPadHeight,oldPadWidth = self.box.getmaxyx()
        if (oldPadHeight < self.height + y | oldPadWidth < self.width + self.x + 2 ):
            self.box.resize( self.height + y, self.width + self.x + 2 )

    def clear(self,stdscr):
        self.placedGatesWin.clear()
        self.toPlaceGateWin.clear()
        self.refresh(stdscr)
    
    def deleteGate(self, gateX, startRail, numRails):
        x = gateXToWinX(gateX)
        y = railToY(startRail)

        for i in range(0,3*numRails):
            self.placedGatesWin.addstr(y-1+i, x, spaces)
        

    def refresh(self,stdscr):
        self.box.erase()
        self._resizeBox(stdscr)
        # self.box.clear()
        self.box.erase()

        self.railsWin.overlay(self.box)
        self.placedGatesWin.overlay(self.box)
        self.toPlaceGateWin.overlay(self.box)

        # keep offset in valid range
        self.yOffset = max(min(self.yOffset, self.height),0)
        self.xOffset = max(min(self.xOffset, self.width-1),0)
        
        self.box.refresh(self.yOffset , self.xOffset, self.y, self.x, self.boxHeight, self.boxWidth)

    def resizeCircuit(self, stdscr, numRails, gateWidths):
        self.placedGatesWin.clear()
        self.toPlaceGateWin.clear()
        self.railsWin.clear()
        self.box.clear()
        self.refresh(stdscr)

        height = railToY(numRails)
        width = gateXToWinX(gateWidths) + circuitLeftMargin

        # size of the entire circuit in rails and gate widths
        # note that this is the size of placedGatesWin, toPlaceGateWin and railsWin
        self.numRails = numRails
        self.gateWidths = gateWidths

        # same as numRails and gateWidths except in rows and cols
        self.width = width
        self.height = height

        # x and y offset of self.box, used for scrolling the window
        self.xOffset = 0
        self.yOffset = 0

        self.placedGatesWin.resize(height, width)
        self.toPlaceGateWin.resize(height, width)
        self.railsWin.resize(height, width)

        # size of the box displayed on screen (note can be smaller than pad self.box, but not larger)
        self.boxHeight = 0
        self.boxWidth  = 0
        
        self._resizeBox(stdscr)

        self._createRailsStr()

        self._createTopNumsStr()
        self.drawRails()

    def drawRails( self ):
        self.railsWin.addstr(0,0,self._xNums)

        for railNum in range(0, self.numRails):
            railY = railToY(railNum)
            self.railsWin.addstr(railY, 0, self._rail)
