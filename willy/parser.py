#!/usr/bin/env python3
from typing import Any
import sys
import copy
from willy import lexer
import ply.yacc as yacc
from willy.stack import Stack
from willy.node import Node
from willy.world import World
from willy.task import Task
from willy.model_procedure import ModelProcedure

"""
    Semantic and Syntactic Analyzer (Parser & Interpreter) for Willy*
"""

# Precedence rules to avoid dangling else ambiguity
precedence = (
    ('left', 'TkThen'),
    ('left', 'TkAnd', 'TkOr', 'TkElse'),
    ('right', 'TkNot', 'TkBegin'),
)

# Required globals from lexer
tokens = lexer.tokens
ParserErrors = []

procedures = ModelProcedure()
newWorld = None
stack = Stack()
stack.push_empty_table()

programBlock = {}    # Optimization: O(1) dictionary mapping block name to its metadata
createdWorlds = {}   # Optimization: O(1) dictionary mapping world ID to World instance
booleansOfWorlds = []
tasks = []

howManyTask = 0
activeWorld = None
currentTask = None

worldInstBool = False
taskBool = False
defineAsBool = False
validateFinalGoal = False
hasSetted = False
isBasketDeclared = False
firstDefineOnTask = False
blockNumber = 0

def p_correctProgram(p):
    "correctProgram : program"
    p[0] = p[1]

def p_program(p):
    """
    program : worldBlock
            | taskBlock
            | worldBlock program
            | taskBlock program
    """
    if len(p) == 2:
        p[0] = Node("Program Block:", [p[1]])
    else:
        p[0] = Node("Program Block:", [p[1], p[2]])

def p_worldInstSet(p):
    """worldInstSet : worldInst worldInstSet
                    | worldInst
    """
    if len(p) == 4:
        p[0] = Node("WorldInstancia:", [p[1], p[3]])
    elif len(p) == 2:
        p[0] = Node("WorldInstancia:", [p[1]])
    else:
        p[0] = Node("WorldInstancia:", [p[1], p[2]])

def p_worldInst(p):
    """ worldInst : worldSet
                | wallSet
                | newObjType
                | setPlaceObjWorld
                | setStartPosition
                | setBasketCapacity
                | newBoolean
                | newGoal
                | finalGoal
    """
    p[0] = Node("WorldInstructions", [p[1]])

def p_wallSet(p):
    """wallSet : TkWall directions TkFrom TkNum TkNum TkTo TkNum TkNum"""
    global newWorld
    actualDir = p[2]

    if actualDir == "north":
        if p[4] == p[7] and p[5] <= p[8]:
            p[0] = Node("WallSet:", [p[2]])
            newWorld.setWall([p[4], p[5]], [p[7], p[8]], actualDir)
        else:
            data_error = {
                "type": "Bad definition of north dimensions",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
    elif actualDir == "south":
        if p[4] == p[7] and p[5] >= p[8]:
            p[0] = Node("WallSet:", [p[2]])
            newWorld.setWall([p[4], p[5]], [p[7], p[8]], actualDir)
        else:
            data_error = {
                "type": "Bad definition of south dimensions",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
    elif actualDir == "west":
        if p[5] == p[8] and p[4] >= p[7]:
            p[0] = Node("WallSet:", [p[2]])
            newWorld.setWall([p[4], p[5]], [p[7], p[8]], actualDir)
        else:
            data_error = {
                "type": "Bad definition of west dimensions",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
    elif actualDir == "east":
        if p[5] == p[8] and p[4] <= p[7]:
            p[0] = Node("WallSet:", [p[2]])
            newWorld.setWall([p[4], p[5]], [p[7], p[8]], actualDir)
        else:
            data_error = {
                "type": "Bad definition of east dimensions",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
    else:
        data_error = {
            "type": "Bad direction token: " + actualDir,
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
        }
        errorSemantic(data_error)

def p_worldDefinition(p):
    """
    worldDefinition : TkBeginWorld ids
    """
    metadata = {
        "type": "World"
    }
    global newWorld
    p[0] = Node("", [p[2]])
    newWorld = World(p[2])
    newWorld.setDimension([1, 1])
    programBlock[p[2]] = metadata
    stack.push({})

def p_worldBlock(p):
    """worldBlock : worldDefinition worldInstSet TkEndWorld
                  | worldDefinition TkEndWorld
    """
    id_world = p[1].children[0]
    global blockNumber
    global validateFinalGoal
    global createdWorlds
    
    attributesObjects = {
        "type": "World",
        "line": p.lineno(2),
        "column": p.lexpos(2) + 1,
    }

    if len(p) == 4:
        p[0] = Node("WorldBlock", [p[2]])
    else:
        p[0] = Node("WorldBlock", [p[2]])

    blockNumber += 1
    validateFinalGoal = False

    if len(stack.stack) > 1:
        stack.pop()
    stack.insert(id_world, attributesObjects)
    createdWorlds[newWorld.id] = newWorld
    
    global hasSetted
    hasSetted = False

    print("###############")
    print("Initial state of " + str(newWorld.id))
    print("Willy Position: " + str(newWorld.getWillyPosition()[0]) + " looking " + str(newWorld.getWillyPosition()[1]))
    print("Basket contents:\n", newWorld.getObjectsInBasket())
    print("Bools state:\n", newWorld.getBools())
    print("Final Goal:\n" + newWorld.getFinalGoal())
    print("Final Goal Value: ", newWorld.getValueFinalGoal())
    print(newWorld)

def p_worldSet(p):
    """worldSet : TkWorld TkNum TkNum
                | empty"""
    global newWorld
    global hasSetted
    if not hasSetted:
        if len(p) == 4:
            if p[2] != 0 or p[3] != 0:
                p[0] = Node("WorldSet", [])
                newWorld.setDimension([p[2], p[3]])
            else:
                data_error = {
                    "type": "0 dimension of World is invalid",
                    "line": p.lineno(2),
                    "column": p.lexpos(2) + 1,
                }
                errorSemantic(data_error)
        else:
            newWorld.setDimension([1, 1])
            p[0] = p[1]
    else:
        data_error = {
            "type": f"To place objects in World: {newWorld.id} need to declare dimensions at start. Cannot replace dimensions.",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
        }
        errorSemantic(data_error)

def p_newObjType(p):
    """newObjType : TkObjType ids TkOf TkColor colors"""
    global newWorld
    id_obj = p[2]

    # O(1) existence check in program blocks dictionary
    if id_obj in programBlock:
        data_error = {
            "type": f"Object '{id_obj}' has name of an existing World or Task",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
        }
        errorSemantic(data_error)
    else:
        p[0] = Node("NewObjectType", [p[2], p[5]])
        attributesObjects = {
            "type": "Object-type",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
            "color": p[5],
        }
        stack.insert(p[2], attributesObjects)
        newWorld.setObjects(id_obj, attributesObjects["color"])

def p_colors(p):
    """colors : TkRed
              | TkBlue
              | TkMagenta
              | TkCyan
              | TkGreen
              | TkYellow
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))

def p_setPlaceObjWorld(p):
    """setPlaceObjWorld : TkPlace TkNum TkOf ids TkAt TkNum TkNum
                        | TkPlace TkNum TkOf ids TkIn TkBasketLower
    """
    global newWorld
    global hasSetted
    global isBasketDeclared
    hasSetted = True
    id_obj = p[4]
    amount = p[2]
    
    if p[2] != 0:
        if len(p) == 8:
            if p[6] > 0 or p[7] > 0:
                p[0] = Node("PlaceObjWorld", [p[4]])
                newWorld.setObjectInWorld(id_obj, amount, [p[6], p[7]])
            else:
                data_error = {
                    "type": "Invalid null position when placing objects",
                    "line": p.lineno(2),
                    "column": p.lexpos(2) + 1,
                }
                errorSemantic(data_error)
        else:
            if isBasketDeclared:
                newWorld.setObjectsInBasket(id_obj, amount)
                p[0] = Node("PlaceObjWorld", [p[4]])
            else:
                data_error = {
                    "type": f"Cannot place elements in a Basket without capacity: {id_obj}",
                    "line": p.lineno(2),
                    "column": p.lexpos(2) + 1,
                }
                errorSemantic(data_error)
    else:
        data_error = {
            "type": "Cannot place 0 objects",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
        }
        errorSemantic(data_error)

def p_setStartPosition(p):
    """setStartPosition : TkStart TkAt TkNum TkNum TkHeading directions """
    global newWorld
    global hasSetted
    hasSetted = True

    if p[3] <= 0 or p[4] <= 0:
        data_error = {
            "type": "Start position (0 or negative) is not valid",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
        }
        errorSemantic(data_error)
    else:
        dimen = newWorld.getDimension()
        if p[3] > dimen[0] or p[4] > dimen[1]:
            data_error = {
                "type": "Willy is out of world bounds",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
        else:
            newWorld.setWillyStart([p[3], p[4]], p[6])
            p[0] = Node("WillyStartPosition", [p[6]])

def p_setBasketCapacity(p):
    """setBasketCapacity : TkBasket TkOf TkCapacity TkNum """
    global newWorld
    global isBasketDeclared
    if p[4] == 0:
        data_error = {
            "type": "Basket capacity of 0 is not allowed",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
        }
        errorSemantic(data_error)
    else:
        isBasketDeclared = True
        newWorld.setCapacityOfBasket(p[4])
        p[0] = Node("BasketCapacity", [])

def p_newBoolean(p):
    """newBoolean : TkBoolean ids TkWith TkInitial TkValue TkTrue
                  | TkBoolean ids TkWith TkInitial TkValue TkFalse
    """
    global newWorld
    p[0] = Node("NewBoolean", [p[2]])
    auxVal = False

    if p[6] == "true":
        auxVal = True
    elif p[6] == "false":
        auxVal = False

    attributesObjects = {
        "type": "Bool",
        "line": p.lineno(2),
        "column": p.lexpos(2) + 1,
        "value": auxVal,
    }
    stack.insert(p[2], attributesObjects)
    newWorld.setBool(p[2], auxVal)
    global booleansOfWorlds
    booleansOfWorlds.append([p[2], attributesObjects])

def p_newGoal(p):
    """newGoal : TkGoal ids TkIs TkWilly TkIs TkAt TkNum TkNum
            | TkGoal ids TkIs TkNum ids TkObjectsLower TkIn TkBasket
            | TkGoal ids TkIs TkNum ids TkObjectsLower TkAt TkNum TkNum
    """
    global newWorld
    if len(p) == 9:
        if p[4] == "willy":
            p[0] = Node("NewGoal", [p[2]])
            attributesObjects = {
                "type": "WillyIsAt",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
                "column_": p[7],
                "row": p[8]
            }
            newWorld.setGoals(p[2], attributesObjects["type"], [p[7], p[8]])
        else:
            p[0] = Node("NewGoal: Object in Basket", [p[2], p[5]])
            attributesObjects = {
                "type": "ObjectInBasket",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
                "amount": p[4],
                "id-object": p[5],
            }
            newWorld.setGoals(p[2], attributesObjects["type"], p[5], p[4])
    else:
        p[0] = Node("NewGoal: Object at position", [p[2], p[5]])
        attributesObjects = {
            "type": "ObjectInPosition",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
            "amount": p[4],
            "id-object": p[5],
            "column_": p[8],
            "row": p[9]
        }
        newWorld.setGoals(p[2], attributesObjects["type"], p[5], p[4], [p[8], p[9]])
        
    stack.insert(p[2], attributesObjects)

def p_finalGoal(p):
    """finalGoal : TkFinalG TkIs finalGoalTest """
    global validateFinalGoal
    if validateFinalGoal:
        data_error = {
            "type": "Only one final goal is allowed",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
        }
        errorSemantic(data_error)
    else:
        p[0] = Node("FinalGoal", [p[3]])
        ret = p[3].finalGoalToString()
        validateFinalGoal = True
        newWorld.setFinalGoal(p[3], ret)

def p_finalGoalTest(p):
    """finalGoalTest : TkParenL finalGoalTest TkParenR
                     | negationGoal
                     | conjunctionGoal
                     | disjunctionGoal
                     | ids
    """
    if len(p) == 2:
        p[0] = Node("FinalGoal", [p[1]])
    else:
        p[0] = Node("Parenthesis", [p[2]])

def p_disjunctionGoal(p):
    """disjunctionGoal : finalGoalTest TkOr finalGoalTest"""
    p[0] = Node("Disjunction", [p[1], p[3]])

def p_conjunctionGoal(p):
    """conjunctionGoal : finalGoalTest TkAnd finalGoalTest"""
    p[0] = Node("Conjunction", [p[1], p[3]])

def p_negationGoal(p):
    """negationGoal : TkNot finalGoalTest"""
    # Optimization: Double Negation Elimination
    if p[2].type == "Not":
        p[0] = p[2].children[0]
    else:
        p[0] = Node("Not", [p[2]])

def p_ids(p):
    "ids : TkId"
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))

def p_taskBlock(p):
    """taskBlock : taskDefinition multiInstructions TkEndTask"""
    global currentTask

    attributesObjects = {
        "type": "Task",
        "line": p.lineno(2),
        "column": p.lexspan(2)[0] + 1,
    }

    p[0] = Node("Task", [p[1], p[2]])

    if len(stack.stack) > 1:
        stack.pop()
    stack.insert(p[1].children[0], attributesObjects)
    
    # Run the task directly if we are in normal CLI execution mode
    # (Dashboard menu handles running explicitly)
    if Task.time != "dashboard":
        print("STARTING TASK EXECUTION")
        p[0].executeMyTask(currentTask)
        print("###############")
        print(f"Final state of world '{currentTask.world.id}' after executing task '{currentTask.id}':")
        print(f"Willy Position: {currentTask.world.getWillyPosition()[0]} looking {currentTask.world.getWillyPosition()[1]}")
        print("Basket contents:\n", currentTask.world.getObjectsInBasket())
        print("Bools state:\n", currentTask.world.getBools())
        print("Final Goal:\n" + currentTask.world.getFinalGoal())
        print("Final Goal Value: ", currentTask.world.getValueFinalGoal())
        print(currentTask.world)
    currentTask.fin = False

def p_taskDefinition(p):
    """
    taskDefinition : TkBeginTask ids TkOn ids
    """
    global activeWorld
    global currentTask
    global howManyTask
    howManyTask += 1

    # O(1) lookup of world in createdWorlds dictionary
    if p[4] in createdWorlds:
        activeWorld = createdWorlds[p[4]]
        newInstanceWorld = copy.deepcopy(activeWorld)

        metadata = {
            "type": "Task"
        }
        p[0] = Node("", [p[2], p[1]])
        programBlock[p[2]] = metadata

        currentTask = Task(p[2], newInstanceWorld)
        tasks.append(currentTask)
        stack.push({})
    else:
        data_error = {
            "type": f"Invalid name of World: '{p[4]}' for task '{p[2]}'",
            "line": p.lineno(2),
            "column": p.lexpos(2) + 1,
        }
        errorSemantic(data_error)

def p_multiInstructions(p):
    """multiInstructions : instructions
                         | empty
                         | instructions TkSemicolon multiInstructions
    """
    if len(p) == 2:
        p[0] = Node("MultiInstruction", [p[1]])
    else:
        p[0] = Node("MultiInstruction", [p[1], p[3]])

def p_primitiveInstructions(p):
    """primitiveInstructions : TkMove
                             | TkTurnL
                             | TkTurnR
                             | TkPick ids
                             | TkDrop ids
                             | TkSet ids
                             | TkSet primitiveBoolean
                             | TkSet primitiveBoolean TkTo TkTrue
                             | TkSet primitiveBoolean TkTo TkFalse
                             | TkSet ids TkTo TkTrue
                             | TkSet ids TkTo TkFalse
                             | TkClear ids
                             | TkClear primitiveBoolean
                             | TkFlip primitiveBoolean
                             | TkFlip ids
                             | TkId
                             | TkTerminate
    """
    global activeWorld
    auxBool = False

    if p[1] == "pick":
        if activeWorld.isObject(p[2]):
            p[0] = Node("Pick", [p[2]])
        else:
            data_error = {
                "type": f"Object '{p[2]}' does not exist in the world",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
    elif p[1] == "drop":
        if activeWorld.isObject(p[2]):
            p[0] = Node("Drop", [p[2]])
        else:
            data_error = {
                "type": f"Object '{p[2]}' does not exist in the world",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
    elif p[1] == "clear":
        if activeWorld.isBool(p[2]):
            p[0] = Node("Clear", [p[2]])
        else:
            data_error = {
                "type": f"Boolean variable '{p[2]}' does not exist in the world",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
    elif p[1] == "flip":
        if activeWorld.isBool(p[2]):
            p[0] = Node("Flip", [p[2]])
        else:
            data_error = {
                "type": f"Boolean variable '{p[2]}' does not exist in the world",
                "line": p.lineno(2),
                "column": p.lexpos(2) + 1,
            }
            errorSemantic(data_error)
    elif p[1] == "set":
        if activeWorld.isBool(p[2]):
            if len(p) == 5:
                if p[4] == "true":
                    auxBool = True
                elif p[4] == "false":
                    auxBool = False
                p[0] = Node("SetBool", [p[2], auxBool])
            else:
                p[0] = Node("SetTrue", [p[2]])
    elif len(p) == 2:
        if p[1] == 'move':
            p[0] = Node("Move", [p[1]])
        elif p[1] == "turn-left":
            p[0] = Node("TL", [p[1]])
        elif p[1] == "turn-right":
            p[0] = Node("TR", [p[1]])
        elif p[1] == "terminate":
            p[0] = Node("Terminate", [p[1]])
        else:
            p[0] = Node("MyInstruction", [p[1]])

def p_booleanTests(p):
    """booleanTests : ids
                    | primitiveBoolean
                    | TkFound TkParenL ids TkParenR
                    | TkCarrying TkParenL ids TkParenR
                    | conjunctionBool
                    | disjunctionBool
                    | negationBool
                    | TkParenL booleanTests TkParenR
                    """
    if len(p) == 2:
        p[0] = Node("BooleanTest", [p[1]])
    elif len(p) == 5:
        if p[1] == "found":
            p[0] = Node("Found", [p[3]])
        elif p[1] == "carrying":
            p[0] = Node("Carrying", [p[3]])
    elif len(p) == 4:
        p[0] = Node("Parenthesis", [p[2]])

def p_disjunctionBool(p):
    """disjunctionBool : booleanTests TkOr booleanTests"""
    p[0] = Node("Disjunction", [p[1], p[3]])

def p_conjunctionBool(p):
    """conjunctionBool : booleanTests TkAnd booleanTests"""
    p[0] = Node("Conjunction", [p[1], p[3]])

def p_negationBool(p):
    """negationBool : TkNot booleanTests"""
    # Optimization: Double Negation Elimination
    if p[2].type == "Not":
        p[0] = p[2].children[0]
    else:
        p[0] = Node("Not", [p[2]])

def p_primitiveBoolean(p):
    """primitiveBoolean : TkFrontCl
                        | TkLeftCl
                        | TkRightCl
                        | TkLookingN
                        | TkLookingE
                        | TkLookingS
                        | TkLookingW
                        """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))

def p_instructions(p):
    """instructions : primitiveInstructions
                    | ifInstruction
                    | TkSemicolon
                    | whileInst
                    | TkBegin multiInstructions TkEnd
                    | TkRepeat TkNum TkTimes instructions
                    | instructionDefineAs instructions
    """
    if len(p) == 2:
        p[0] = Node("Instructions", [p[1]])
    elif len(p) == 3:
        p[0] = Node("Define As", [p[1], p[2]])
        attributesObjects = {
            "type": "Instruction",
            "line": p.lineno(1),
            "column": p.lineno(1) + 1,
        }
        stack.pop()
        stack.insert(p[1].children[0], attributesObjects)
    elif len(p) == 4:
        p[0] = Node("Begin", [p[2]])
    elif len(p) == 5:
        if p[1] == "repeat":
            if p[2] <= 0:
                data_error = {
                    "type": f"Bad number of iterations for repeat: {p[2]}",
                    "line": p.lineno(2),
                    "column": p.lexpos(2) + 1,
                }
                errorSemantic(data_error)
            else:
                p[0] = Node("Repeat", [p[2], p[4]])

def p_ifInstruction(p):
    """ ifInstruction : TkIf booleanTests TkThen instructions
                      | TkIf booleanTests TkThen instructions TkElse instructions
    """
    if len(p) == 5:
        p[0] = Node('ifSimple', [p[2], p[4]])
    else:
        p[0] = Node('ifCompound', [p[2], p[4], p[6]])

def p_whileInst(p):
    """ whileInst : TkWhile booleanTests TkDo instructions
    """
    p[0] = Node('whileInst', [p[2], p[4]])

def p_instructionDefineAs(p):
    """instructionDefineAs : TkDefine ids TkAs"""
    p[0] = Node("Define as", [p[2]])
    stack.push({})

def p_directions(p):
    """directions : TkNorth
                | TkEast
                | TkSouth
                | TkWest
    """
    p[0] = p[1]

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    global ParserErrors
    if p is not None:
        error = f'Syntax error "{p.value}" at line {p.lineno}'
        ParserErrors.append(error)
        print(ParserErrors, file=sys.stderr)
    else:
        print("Syntax error at EOF", file=sys.stderr)
    sys.exit(1)

def errorSemantic(err):
    global ParserErrors
    if err is not None:
        error = f'Semantic error: {err["type"]} at line {err["line"]}'
        ParserErrors.append(error)
        print(ParserErrors, file=sys.stderr)
    else:
        print("Syntax error at EOF", file=sys.stderr)
    sys.exit(1)
