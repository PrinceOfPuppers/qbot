
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

def drawRails( railsWin, numRails ):
    wy, wx = railsWin.getmaxyx()
    rail = wx*horizontalLine
    for railNum in range(0, numRails):
        railY = 3*railNum + 1
        railsWin.addstr(railY, 0, rail)

    railsWin.refresh()


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
            scr.addstr(topOfGate + i*3 + j + 2, leftOfGate, mid)
    
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
        
    circuitWin.refresh()


import curses

def main(stdscr):
    curses.use_default_colors()
    curses.can_change_color() == False
    # curses.init_pair(1, curses.COLOR_WHITE, -1)
    numRails = 5
    stdscr = curses.initscr()
    circuitWinX = 1
    circuitWinY = 0
    circuitWinCols = 30
    circuitWinLines =  numRails*3 + 2
    circuitWin = curses.newwin(circuitWinLines, circuitWinCols, circuitWinY, circuitWinX)
    railsWin =curses.newwin(circuitWinLines, circuitWinCols, circuitWinY, circuitWinX)


    drawRails(railsWin, numRails)
    drawGate(circuitWin,0,1,1,'H',[0,2,3])
    circuitWin.overlay(railsWin)
    railsWin.refresh()
    circuitWin.refresh()
    # circuitWin.addstr(4,3,"hello")
    # circuitWin.refresh()
    stdscr.refresh()





    # drawGate(scr,(0,0),0,1,1,'H',[])
    stdscr.getch()
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)