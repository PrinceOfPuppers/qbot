
'''
┌───┐
│ H │
└───┘
'''
top = "┌───┐"
mid = "│   │" 
bottom = "└───┘"

oneQubitMeasurement = "◁ "
control = "●"
vertLine = "│"

circuitLeftMargin = 3

def drawGate(scr, circuitCorner: (int, int),
             gateX: int, gatefirstRail: int, gateNumRails: int, gateSymbol: int, gateControls:[int]):
    '''
    circuitDiagramCorner is the top left hand corner of the circuit diagram 
    '''
    cx,cy = circuitCorner
    leftOfGate = cx + gateX + circuitLeftMargin -2
    firstRail = cy + gatefirstRail*3 
    scr.addstr(firstRail, leftOfGate, top)
    scr.addstr(firstRail+1, leftOfGate, mid)

    for i in range(0,gateNumRails-1):
        for j in range(0,3):
            scr.addstr(firstRail + i*3 + j + 2, leftOfGate, mid)
    
    scr.addstr(firstRail + 3*(gateNumRails-1) + 2, leftOfGate, bottom)

    scr.addch((firstRail -1 + (3*gateNumRails + 1)//2),leftOfGate+2,gateSymbol)

    scr.refresh()



if __name__ == "__main__":
    import curses
    scr = curses.initscr()
    drawGate(scr,(0,0),0,0,1,'H',[])
    drawGate(scr,(0,0),0,1,1,'H',[])
    scr.getch()
    curses.endwin()