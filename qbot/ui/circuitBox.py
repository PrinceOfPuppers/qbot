import curses
import curses.panel

horizontalLine = "─"

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
    "  V  " ,
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
        'spaceUnderneath',
        'placedGatesWin',
        'toPlaceGateWin',
        'railsWin',
        'box',
        '_rail',
        '_xNumsList',
        '_xNums'
    )
    def __init__(self, y, x, numRails, gateWidths, spaceUnderneath):
        '''
        spaceUnderneath is how much of the terminal should be left for other ui elements
        '''
        height = railToY(numRails)
        width = gateXToWinX(gateWidths) +30

        self.numRails = numRails
        self.gateWidths = gateWidths

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.xOffset = 0
        self.yOffset = 0
        self.spaceUnderneath = spaceUnderneath

        self.placedGatesWin = curses.newwin(height, width, y, x)
        self.toPlaceGateWin = curses.newwin(height, width, y, x)
        self.railsWin = curses.newwin(height, width, y, x)
        self.box = curses.newpad(height, width)

        self._createRailsStr()

        self._xNumsList = [circuitLeftMargin*" "+"0"]
        self._createTopNumsStr()

    def _createTopNumsStr(self):
        currentLen = len(self._xNumsList)
        newLen = (self.width -  circuitLeftMargin)//(xToColFactor)
        if newLen > currentLen:
            for i in range(currentLen,newLen):
                num = str(i)
                self._xNumsList.append((xToColFactor-len(num))*" " + num)

        self._xNums = "".join(self._xNumsList[0:newLen])

    def _createRailsStr(self):
        self._rail = self.width*horizontalLine

    def refresh(self,stdscr):
        y,x = stdscr.getmaxyx()
        boxWidth = x - 1
        boxHeight = y - self.spaceUnderneath - 1

        boxWidth = min(self.width,boxWidth) 
        boxHeight = min(self.height,boxHeight)
        if self.yOffset > self.height - boxHeight:
            self.yOffset = self.height - boxHeight
            self.yOffset = max(0,self.yOffset)
        if self.xOffset >= self.width - boxWidth:
            self.xOffset = self.width - boxWidth
            self.xOffset = max(0,self.xOffset)

        self.box.clear()

        self.railsWin.overlay(self.box)
        self.placedGatesWin.overlay(self.box)
        self.toPlaceGateWin.overlay(self.box)

        self.box.refresh(self.yOffset,self.xOffset,self.y,self.x, boxHeight, boxWidth)

    
    def resizeCircuit(self, numRails, gateWidths):
        '''
        change the number of rails or the width of the circuit in units of gate widths
        -1 for either parameter will leave it as it is
        '''
        height = self.height if numRails == -1 else railToY(numRails)
        width = self.width if gateWidths == -1 else gateXToWinX(gateWidths)
        
        self.height = height
        self.width = width

        self.railsWin.resize(height,width)
        self.placedGatesWin.resize(height,width)
        self.toPlaceGateWin.resize(height, width)

        self._createTopNumsStr()
        self._createRailsStr()
        self.drawRails()

    def drawRails( self ):
        self.railsWin.addstr(0,0,self._xNums)

        for railNum in range(0, self.numRails):
            railY = railToY(railNum)
            self.railsWin.addstr(railY, 0, self._rail)

