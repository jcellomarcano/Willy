#!/usr/bin/env python3
"""
    Lexical Analyzer for the Willy* Language
"""

from ply import lex

# Collection of invalid tokens encountered during lexing
InvalidTokens = []

# Reserved Words
tokens = [
    'TkBeginWorld',
    'TkEndWorld',
    'TkObjType',
    'TkTurnL',
    'TkTurnR',
    'TkFrontCl',
    'TkLeftCl',
    'TkRightCl',
    'TkLookingN',
    'TkLookingE',
    'TkLookingS',
    'TkLookingW',
    'TkFinalG',
    'TkBeginTask',
    'TkEndTask',

    # Separators and identifiers
    'TkSemicolon',
    'TkTab',
    'TkId',
    'TkNum',
    'TkParenL',
    'TkParenR',
]

reserved = {
    # Willy's Words / functions
    'World': 'TkWorld',
    'Wall': 'TkWall',
    'Place': 'TkPlace',
    'Start': 'TkStart',
    'Basket': 'TkBasket',
    'Boolean': 'TkBoolean',
    'Goal': 'TkGoal',

    # Common Words / Operators
    'from': 'TkFrom',
    'to': 'TkTo',
    'of': 'TkOf',
    'color': 'TkColor',
    'at': 'TkAt',
    'in': 'TkIn',
    'is': 'TkIs',
    'on': 'TkOn',
    'heading': 'TkHeading',
    'with': 'TkWith',
    'initial': 'TkInitial',
    'value': 'TkValue',
    'capacity': 'TkCapacity',
    'basket': 'TkBasketLower',
    'objects': 'TkObjectsLower',

    # Colors
    'red': 'TkRed',
    'blue': 'TkBlue',
    'magenta': 'TkMagenta',
    'cyan': 'TkCyan',
    'green': 'TkGreen',
    'yellow': 'TkYellow',

    # Directions
    'north': 'TkNorth',
    'east': 'TkEast',
    'south': 'TkSouth',
    'west': 'TkWest',

    # Conditionals
    'if': 'TkIf',
    'else': 'TkElse',
    'then': 'TkThen',

    # Loops
    'repeat': 'TkRepeat',
    'while': 'TkWhile',
    'times': 'TkTimes',

    # Auxiliaries
    'define': 'TkDefine',
    'as': 'TkAs',
    'do': 'TkDo',

    # Willy's Actions
    'willy': 'TkWilly',
    'move': 'TkMove',
    'pick': 'TkPick',
    'drop': 'TkDrop',
    'set': 'TkSet',
    'clear': 'TkClear',
    'flip': 'TkFlip',
    'terminate': 'TkTerminate',
    'found': 'TkFound',
    'carrying': 'TkCarrying',

    # Boolean Values
    'true': 'TkTrue',
    'false': 'TkFalse',
    'or': 'TkOr',
    'and': 'TkAnd',
    'not': 'TkNot',

    # Blocks
    'begin': 'TkBegin',
    'end': 'TkEnd',
}

# Add reserved words to the token list
tokens += list(reserved.values())

# Token rules
t_TkSemicolon = r';'
t_TkParenL = r'\('
t_TkParenR = r'\)'

# Ignored characters
t_ignore_TkCommentsBlock = r'{{(.|\n)[^{}]*}}'
t_ignore_TkComments = r'[\-]{2}.*'
t_ignore_TkSpace = r'\s'
t_ignore_TkTab = r' \t'

def t_TkBeginWorld(t):
    r'begin\-world'
    return t

def t_TkEndWorld(t):
    r'end\-world'
    return t

def t_TkObjType(t):
    r'Object\-type'
    return t

def t_TkTurnL(t):
    r'turn\-left'
    return t

def t_TkTurnR(t):
    r'turn\-right'
    return t

def t_TkFrontCl(t):
    r'front\-clear'
    return t

def t_TkLeftCl(t):
    r'left\-clear'
    return t

def t_TkRightCl(t):
    r'right\-clear'
    return t

def t_TkLookingN(t):
    r'looking\-north'
    return t

def t_TkLookingE(t):
    r'looking\-east'
    return t

def t_TkLookingS(t):
    r'looking\-south'
    return t

def t_TkLookingW(t):
    r'looking\-west'
    return t

def t_TkFinalG(t):
    r'Final[\s]+goal'
    return t

def t_TkBeginTask(t):
    r'begin\-task'
    return t

def t_TkEndTask(t):
    r'end\-task'
    return t

def t_newLine(line):
    r'\n+'
    line.lexer.lineno += len(line.value)

# Error handler for illegal characters
def t_error(t):
    """ Default error handler for invalid tokens """
    error_msg = f'Illegal character "{t.value[0]}" at line {t.lineno}, column {t.lexpos + 1}'
    InvalidTokens.append(error_msg)
    t.lexer.skip(1)

def t_TkId(t):
    r'[a-zA-Z]+[0-9]*[a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'TkId')
    return t

def t_TkNum(t):
    r'\d+'
    t.value = int(t.value)
    return t
