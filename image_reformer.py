import cv2
import numpy as np
import queue
import time

# Board Layout
#-------------
#  \Q3 | Q5/
#   \  |  /
#    \ | /   
# Q2 / | \ Q4
#   /  |  \
#  /Q1 | Q6\

image_prefix = 'images/'
#background = cv2.imread(f'{image_prefix}board.png')
# define the height and width of the background image
bg_height, bg_width, _ = background = cv2.imread(f'{image_prefix}board.jpg').shape

piece_types = {
    'P':'white_pawn.png', 'R':'white_rook.png', 'N':'white_knight.png', 'B':'white_bishop.png', 'Q':'white_queen.png', 'K':'white_king.png',
    'p':'black_pawn.png', 'r':'black_rook.png', 'n':'black_knight.png', 'b':'black_bishop.png', 'q':'black_queen.png', 'k':'black_king.png',
    'W':'red_pawn.png', 'C':'red_rook.png', 'H':'red_knight.png', 'S':'red_bishop.png', 'U':'red_queen.png', 'I':'red_king.png'
}

#OG
Q1 = {  'A': {1:(253,712), 2:(230,665), 3:(209,611), 4:(188,564)},
        'B': {1:(308,709), 2:(292,647), 3:(277,585), 4:(262,525)},
        'C': {1:(363,703), 2:(353,631), 3:(345,560), 4:(334,486)},
        'D': {1:(417,699), 2:(413,616), 3:(412,533), 4:(408,446)}
    }
    #OG
Q2 = {  'A': {5:(161,516), 6:(126,471), 7:(96,426), 8:(63,383)},
        'B': {5:(232,469), 6:(185,427), 7:(141,380), 8:(96,335)},
        'C': {5:(301,425), 6:(242,380), 7:(186,337), 8:(127,294)},
        'D': {5:(370,381), 6:(300,339), 7:(230,295), 8:(159,247)}
    }

#Q4 flipped vertically
Q3 = {  'L': {8:(253, 52), 7:(308, 57), 6:(363, 61), 5:(417,67)},
        'K': {8:(231, 104), 7:(292, 118), 6:(350, 135), 5:(412, 152)},
        'J': {8:(207, 151), 7:(276, 178), 6:(341, 210), 5:(409, 235)},
        'I': {8:(182, 202), 7:(259, 240), 6:(334, 282), 5:(406, 317)}
    }
Q4 = {  'H': {9:(bg_width - 161,516), 10:(bg_width - 126,471), 11:(bg_width - 96,426), 12:(bg_width - 63,383)},
        'G': {9:(bg_width - 232,469), 10:(bg_width - 185,427), 11:(bg_width - 141,380), 12:(bg_width - 96,335)},
        'F': {9:(bg_width - 301,425), 10:(bg_width - 242,380), 11:(bg_width - 186,337), 12:(bg_width - 127,294)},
        'E': {9:(bg_width - 370,381), 10:(bg_width - 300,339), 11:(bg_width - 230,295), 12:(bg_width - 159,247)}
    }

Q5 = {  'L': {12:(bg_width - 253, 52), 11:(bg_width - 308, 57), 10:(bg_width - 363, 61), 9:(bg_width - 417,67)},
        'K': {12:(bg_width - 231, 104), 11:(bg_width - 292, 118), 10:(bg_width - 350, 135), 9:(bg_width - 412, 152)},
        'J': {12:(bg_width - 207, 151), 11:(bg_width - 276, 178), 10:(bg_width - 341, 210), 9:(bg_width - 409, 235)},
        'I': {12:(bg_width - 182, 202), 11:(bg_width - 259, 240), 10:(bg_width - 334, 282), 9:(bg_width - 406, 317)}
    }
Q6 = {  'H': {1:(bg_width - 253,712), 2:(bg_width - 230,665), 3:(bg_width - 209,611), 4:(bg_width - 188,564)},
        'G': {1:(bg_width - 308,709), 2:(bg_width - 292,647), 3:(bg_width - 277,585), 4:(bg_width - 262,525)},
        'F': {1:(bg_width - 363,703), 2:(bg_width - 353,631), 3:(bg_width - 345,560), 4:(bg_width - 334,486)},
        'E': {1:(bg_width - 417,699), 2:(bg_width - 413,616), 3:(bg_width - 412,533), 4:(bg_width - 408,446)}
    }

def get(letter,number):
    #A-D
    if letter in Q1.keys():
        if number >= 1 and number <= 4:
            return Q1[letter][number]
        if number >= 5 and number <= 8:
            return Q2[letter][number]

    #I-L
    if letter in Q3.keys():
        if number >= 5 and number <= 8:
            return Q3[letter][number]
        if number >= 9 and number <= 12:
            return Q5[letter][number]

    #E-H
    if letter in Q4.keys():
        if number >= 1 and number <= 4:
            return Q6[letter][number]
        if number >= 9 and number <= 12:
            return Q4[letter][number]

#pieces = []
def place(background, pieces):
    foreground = None
    mask = None
    mask_inv = None
    foreground_bg = None
    roi_bg = None
    dst = None 
    #background = None
    for piece in pieces:
        #print(str((piece[0],piece[1])))
        #print(str(get(piece[0],piece[1])))
        center_x, center_y = get(piece[0],piece[1])

        # Load the images
        foreground = cv2.imread(f'{image_prefix}{piece_types[piece[2]]}')

        # define the region of interest (ROI)
        rows, cols, channels = foreground.shape
        roi_x = center_x - int(cols / 2)
        roi_y = center_y - int(rows / 2)
        roi = background[roi_y:roi_y+rows, roi_x:roi_x+cols]

        # create a mask for the foreground image
        foreground_gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(foreground_gray, 250, 255, cv2.THRESH_BINARY_INV)

        # invert the mask
        mask_inv = cv2.bitwise_not(mask)

        # apply the mask to the foreground image
        foreground_bg = cv2.bitwise_and(foreground, foreground, mask=mask)

        # apply the inverted mask to the region of interest (ROI)
        roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

        # combine the foreground and background using the add function
        dst = cv2.add(roi_bg, foreground_bg)

        background[roi_y:roi_y+rows, roi_x:roi_x+cols] = dst
    return background, pieces

# display the resulting image
def display(background, mode=1):
    cv2.imshow("Result", background)
    cv2.waitKey(mode)
    time.sleep(0.5)
    cv2.destroyAllWindows()

def test():
    def load(shard):
        for i in shard.keys():
            for j in shard[i].keys():
                pieces.append((i,j,'p'))
        place(shard)
    load(Q1)
    load(Q2)
    load(Q3)
    load(Q4)
    load(Q5)
    load(Q6)

    display()
    pieces.clear()
    background = cv2.imread(f'{image_prefix}board.png')

def startboardtest(pieces=[]):
    lookup = {}
    def pawncreator(row, piece, order, pieces, lookup):
        for i in order:
            pieces.append((i, row, piece))
            lookup[(i,row)] = (i, row, piece)
        return pieces, lookup

    #Red are A-H rows 1 and 2(pawns)
    order = ['A','B','C','D','E','F','G','H']
    pieces, lookup = pawncreator(2,'W',order, pieces, lookup)
    row = 1
    pieces.append((order[0], row, 'C'))
    lookup[(order[0], row)] = (order[0], row, 'C')
    pieces.append((order[1], row, 'H'))
    lookup[(order[1], row)] = (order[1], row, 'H')
    pieces.append((order[2], row, 'S'))
    lookup[(order[2], row)] = (order[2], row, 'S')
    pieces.append((order[3], row, 'I'))
    lookup[(order[3], row)] = (order[3], row, 'I')
    pieces.append((order[4], row, 'U'))
    lookup[(order[4], row)] = (order[4], row, 'U')
    pieces.append((order[5], row, 'S'))
    lookup[(order[5], row)] = (order[5], row, 'S')
    pieces.append((order[6], row, 'H'))
    lookup[(order[6], row)] = (order[6], row, 'H')
    pieces.append((order[7], row, 'C'))
    lookup[(order[7], row)] = (order[7], row, 'C')

    #Black are HGFEIJKL 12 and 11(pawns)
    order = ['H','G','F','E','I','J','K','L']
    pieces, lookup = pawncreator(11, 'p', order, pieces, lookup)
    row = 12
    pieces.append((order[0], row, 'r'))
    lookup[(order[0], row)] = (order[0], row, 'r')
    pieces.append((order[1], row, 'n'))
    lookup[(order[1], row)] = (order[1], row, 'n')
    pieces.append((order[2], row, 'b'))
    lookup[(order[2], row)] = (order[2], row, 'b')
    pieces.append((order[3], row, 'k'))
    lookup[(order[3], row)] = (order[3], row, 'k')
    pieces.append((order[4], row, 'q'))
    lookup[(order[4], row)] = (order[4], row, 'q')
    pieces.append((order[5], row, 'b'))
    lookup[(order[5], row)] = (order[5], row, 'b')
    pieces.append((order[6], row, 'n'))
    lookup[(order[6], row)] = (order[6], row, 'n')
    pieces.append((order[7], row, 'r'))
    lookup[(order[7], row)] = (order[7], row, 'r')

    #White is LKJIDCBA rows 8 and 7(pawns)
    order = ['L','K','J','I','D','C','B','A']
    pieces, lookup = pawncreator(7, 'P', order, pieces, lookup)
    row = 8
    pieces.append((order[0], row, 'R'))
    lookup[(order[0], row)] = (order[0], row, 'R')
    pieces.append((order[1], row, 'N'))
    lookup[(order[1], row)] = (order[1], row, 'N')
    pieces.append((order[2], row, 'B'))
    lookup[(order[2], row)] = (order[2], row, 'B')
    pieces.append((order[3], row, 'K'))
    lookup[(order[3], row)] = (order[3], row, 'K')
    pieces.append((order[4], row, 'Q'))
    lookup[(order[4], row)] = (order[4], row, 'Q')
    pieces.append((order[5], row, 'B'))
    lookup[(order[5], row)] = (order[5], row, 'B')
    pieces.append((order[6], row, 'N'))
    lookup[(order[6], row)] = (order[6], row, 'N')
    pieces.append((order[7], row, 'R'))
    lookup[(order[7], row)] = (order[7], row, 'R')

    background = cv2.imread(f'{image_prefix}board.jpg')
    background, pieces = place(background, pieces)
    return background, pieces, lookup

def remove(piece, pieces):
    pieces.remove(piece)
    background = cv2.imread(f'{image_prefix}board.jpg')
    background, pieces = place(background,pieces)
    return background, pieces

#test function
def deleteTest():
    order = ['L','K','J','I','D','C','B','A']
    row = 8
    
    pieces.append((order[4], row, 'Q'))
    pieces.append((order[7], row, 'R'))

    place()
    display()

    #print(str(pieces))
    pieces.remove((order[4], row, 'Q'))
    #print(str(pieces))
    background = cv2.imread(f'{image_prefix}board.png')


    background = place(background)
    cv2.imshow("Result", background)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()

#test function
def simulateMoves():
    order = ['L','K','J','I','D','C','B','A']
    row = 8
    background = cv2.imread(f'{image_prefix}board.jpg')
    pieces = []

    pieces.append((order[4], row, 'Q'))
    pieces.append((order[7], row, 'R'))
    background, pieces = place(background, pieces)
    display(background)

    background, pieces = remove(piece=(order[4], row, 'Q'), pieces=pieces)

    pieces.append((order[4], 7, 'Q'))
    background, pieces = place(background=background, pieces=pieces)
    display(background)
    background, pieces = remove(piece=(order[4], 7, 'Q'), pieces=pieces)

    pieces.append((order[4], 6, 'Q'))
    background, pieces = place(background=background, pieces=pieces)
    display(background)
    background, pieces = remove(piece=(order[4], 6, 'Q'), pieces=pieces)

    pieces.append((order[4], 5, 'Q'))

    background, pieces = place(background, pieces)
    display(background)
    background, pieces = remove(piece=(order[4], 5, 'Q'), pieces=pieces)

    moves = [('I', 5, 'Q'),('I', 9, 'Q'),('E', 9, 'Q'),('E', 4, 'Q'),('D', 4, 'Q'),('D', 5, 'Q')]
    i=0

    while(True):
        pieces.append(moves[i])
        background, pieces = place(background=background, pieces=pieces)
        display(background)
        background, pieces = remove(piece=moves[i], pieces=pieces)
        if i == 5:
            i = 0
        else:
            i += 1

#startboardtest()
#simulateMoves()

def interpretFEN(fen, lookup, background=cv2.imread(f'{image_prefix}board.jpg'), pieces=[]):
    old = None
    new = None
    Upgrade = None
    if len(fen) == 4:
        old = fen[:2]
        new = fen[2:4]
    if len(fen) == 5:
        Upgrade = fen[-1]
        old = fen[:2]
        new = fen[2:4]
    print(f'old:{old}, new:{new}, upgrade:{Upgrade}')
    var1 = 0
    if old[1] == 'a': var1 = 10
    elif old[1] == 'b': var1 = 11
    elif old[1] == 'c': var1 = 12
    else:
        var1 = int(old[1])

    try:
        background, pieces = remove(piece=(str(old[0]).upper(), int(var1),lookup[(str(old[0]).upper(),int(var1))][2]), pieces=pieces)
    except:
        pass
    
    var = 0
    if new[1] == 'a': var = 10
    elif new[1] == 'b': var = 11
    elif new[1] == 'c': var = 12
    else:
        var = int(new[1])

    if Upgrade is not None:
        pieces.append((str(old[0]).upper(), var, Upgrade))
        lookup[(str(old[0]).upper(),int(var))] = (str(old[0]).upper(), var, Upgrade)
    else:
        pieces.append((str(old[0]).upper(), var, lookup[(str(old[0]).upper(),int(var1))][2]))
        lookup[(str(old[0]).upper(),int(var))] = (str(old[0]).upper(), var, lookup[(str(old[0]).upper(),int(var1))][2])
    background, pieces = place(background=background, pieces=pieces)
    display(background, mode=0)
    return lookup, pieces, background


def repl():
    background = cv2.imread(f'{image_prefix}board.jpg')
    background, pieces, lookup = startboardtest()
    display(background, mode=0)
    while True:
        #display(background)
        user_input = input('>> ') # prompt user for input
        
        try:
            if user_input == 'exit':
                exit()
            if user_input == 'show':
                display(background, mode=0)
            else:
                lookup, pieces, background = interpretFEN(fen=user_input, lookup=lookup, pieces=pieces,background=background)

        except Exception as e:
            print(f"Error: {e}") # handle errors gracefully
repl()



# interpretFEN('e2e4')
# interpretFEN('ibicQ')

