import curses
import curses.panel

seperator = '═'

class SelectedBox:
    __slots__ = (
        'width',
        'height',
        'firstCol',
        'boxLabel',
        'text',
        'splitChar',
        'leftRightPad'
    )

    def __init__(self, stdscr, height, text = '', boxLabel = 'Selected State: ', splitChar = ' '):
        self.height = height
        self.resize(stdscr)
        self.boxLabel = boxLabel
        self.splitChar = splitChar
        self.text = text
        self.leftRightPad = 1

    def resize(self, stdscr):
        screenHeight, self.width = stdscr.getmaxyx()
        self.firstCol = screenHeight - self.height - 1
    
    def refresh(self, stdscr):
        self.resize(stdscr)
        stdscr.addstr(self.firstCol,0, self.width*seperator)
        stdscr.addstr(self.firstCol+1, 1, self.boxLabel)
        
        splitText = []
        i = 0
        # find appropreate places to break text
        while True:
            i = self.text.find(self.splitChar, i)
            if i<0:
                break
            splitText.append(i)
            i += 1
            


        i=0
        start = 0
        lineNum = self.firstCol+2
        while True:
            split = splitText[i]
            if split - start > self.width - 2*self.leftRightPad:
                stdscr.addstr(lineNum,1, self.text[start:splitText[i-1]])
                start = splitText[i-1]+1
                lineNum+=1

            if lineNum > self.height + self.firstCol:
                break

            i+=1

            if i == len(splitText):
                stdscr.addstr(lineNum,1, self.text[start:])
                break



        stdscr.refresh()