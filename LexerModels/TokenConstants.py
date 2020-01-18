"""
Clase encargada de llevar todos los tokens:
Palabras Reservadas
Funciones
I/O
Arreglo de los tokens declarados
Especificaciones de los mismos
"""

from ply import lex

# Reserved Words
reservedWords = {
    # Wily's Words / functions
    'begin-world': 'TkBeginWorld',
    'end-world': 'TkEndWorld',
    'World': 'TkWorld',
    'Wall': 'TkWall',
    'Object-type': 'TkObjType',
    'Place': 'TkPlace',
    'Start': 'TkStart',
    'Basket': 'TkBasket',
    'Boolean': 'TkBoolean',
    'Goal': 'TkGoal',
    'Final': 'TkFinal',

    # Common Words - Oper - Used on previous words to build a instruction
    'from': 'TkFrom',
    'to': 'TkTo',
    'of': 'TkOf',
    'color': 'TkColor',
    'at': 'TkAt',
    'in': 'TkIn',
    'is': 'TkIs',
    'heading': 'TkHeading',
    # No se como ejemplificar: with initial value - se usa con Boolean

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

    # Willy's Work Words

    # Data Type
    # 'int': 'TkInt',     # No se si lo vamos a usar
    'bool': 'TkBool',   # Entendi que hay 2 tipos de boolean

    # Conditionals
    'if': 'TkIf',
    'fi': 'Tkfi',
    'else': 'TkElse',
    'then': 'TkThen',

    # Loops
    'for': 'TkFor',
    'repeat': 'TkRepeat',
    'while': 'TkWhile',
    'times': 'TkTimes',

    # Aux
    'define': 'TkDefine',
    'begin': 'TkBegin',
    'end': 'TkEnd',
    'as': 'TkAs',
    #'and': 'TkAnd',
    #'or': 'TkOr',
    #'not': 'TkNot',

    # Willy's Actions
    'move': 'TkMove',
    'turn-left': 'TkTurnL',
    'turn-right': 'TkTurnR',
    'pick': 'TkPick',
    'drop': 'TkDrop',
    'set': 'TkSet',
    'clear': 'TkClear',
    'flip': 'TkFlip',
    'terminate': 'TkTerminate',
    'found': 'TkFound',
    'carrying': 'TkCarrying',

    # Booleans Primitives
    'front-clear': 'TkFrontCl',
    'left-clear': 'TkLeftCl',
    'right-clear': 'TkRightCl',
    'looking-north': 'TkLookingN',
    'looking-east': 'TkLookingE',
    'looking-south': 'TkLookingS',
    'looking-west': 'TkLookingW',

    # Boolean Values
    'true': 'TkTrue',
    'false': 'TkFalse',
}
# Token's Lsit
tokens = [
    # Para las variables
    'TkId',

    #  Numeros enteros
    'TkNum',

    # Cadenas de Caracteres
    'TkString',

    # Simbolos utilizados para denotar separadores
    'TkOBlock',
    'TkCBlock',
    'TkSoForth',
    'TkComma',
    'TkCOpenPar',
    'TkClosePar',
    'TkAsig',
    'TkSemicolon',
    #'TkArrow',

    # Simbolos utiliados para denotar operadores
    #'TkPlus',
    #'TkMinus',
    #'TkMult',
    #'TkDiv',
    #'TkMod',
    'TkOr',
    'TkAnd',
    'TkNot',
    #'TkLess',
    #'TkLeq',
    #'TkGeq',
    #'TkGreater',
    'TkEqual',
    'TkNEqual',
    'TkOBracket',
    'TkCBracket',
    'TkTwoPoints',
    'TkConcat',
] + list(reservedWords.values())

# Especificaciones de los tokens
t_TkOBlock = r'\|\['
t_TkCBlock = r'\]\|'
t_TkSoForth = r'\.\.'
t_TkComma = r'\,'
t_TkCOpenPar = r'\('
t_TkClosePar = r'\)'
t_TkSemicolon = r';'

"""
t_TkPlus = r'\+'
t_TkMinus = r'\-'
t_TkMult = r'\*'
t_TkDiv = r'\/'
t_TkMod = r'\%'
t_TkOr = r'\/'
t_TkAnd = r'\/'
t_TkNot = r'\!'
t_TkLess = r'<'
t_TkLeq = r'<='
t_TkGeq = r'>='
t_TkGreater = r'>'
t_TkEqual = r'=='
t_TkNEqual = r'!='
"""
t_TkOBracket = r'\['
t_TkCBracket = r'\]'
t_TkConcat = r'\|\|'

# Ignored Chars
t_ignore_Space = r'\s'             # Space
# t_ignore_Comment = r'.*'        # Comentarios - falta colocar el regex de {{}}
t_ignore_Line = r' \n'             # Salto de linea
t_ignore_Tab = r' \t'              # Tabuladores


ValidTokens = []                #Coleccion de tokens validos
InvalidTokens = []              #Coleccion de tokens invalidos

# Prove of import Functions (This class is ony for tokens, don't declare functions here) - Main is Lexer
def outHello():
    print("Estamos conectando correctamente")
