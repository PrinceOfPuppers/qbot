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
    return xToColFactor*x + circuitLeftMargin -2

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

        for i in range(1,(self.width)//(xToColFactor-1) - circuitLeftMargin):
            self._xNums.append(str(i))
        self._xNums = ((xToColFactor-1)*" ").join(self._xNums)
    
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

