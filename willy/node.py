#!/usr/bin/env python3
from __future__ import annotations
import time
from willy.world import World
from willy.task import Task

"""
    Node representing a node in the Abstract Syntax Tree (AST).
    Provides methods to evaluate conditions and execute simulation blocks.
"""

class Node:
    def __init__(self, type: str, children: list[Node | str | int | bool] | None = None):
        self.type = type
        self.children = children if children is not None else []
        self.index = None  # Sequential ID assigned dynamically during AST analysis

    def assign_indices(self, start_index: int = 1) -> int:
        """ Recursively assign sequential integer indices to all Nodes in the AST """
        self.index = start_index
        current = start_index + 1
        for child in self.children:
            if isinstance(child, Node):
                current = child.assign_indices(current)
        return current

    def __str__(self, level: int = 0) -> str:
        index_str = f"[{self.index}] " if self.index is not None else ""
        ret = "  " * level + index_str + self.type + "\n"
        for child in self.children:
            if isinstance(child, Node):
                ret += child.__str__(level + 1)
            else:
                ret = ret.rstrip("\n")
                ret += " " + str(child) + "\n"
        return ret

    def finalGoalToString(self) -> str:
        match self.type:
            case "Conjunction":
                return self.children[0].finalGoalToString() + " and " + self.children[1].finalGoalToString()
            case "Disjunction":
                return self.children[0].finalGoalToString() + " or " + self.children[1].finalGoalToString()
            case "Parenthesis":
                return "(" + self.children[0].finalGoalToString() + ")"
            case "Not":
                return "not " + self.children[0].finalGoalToString()
            case _:
                ret = ""
                for child in self.children:
                    if isinstance(child, Node):
                        ret += child.finalGoalToString()
                    else:
                        ret = ret.rstrip("\n")
                        ret += str(child)
                return ret

    def finalGoalValue(self, world: World, mybool: bool) -> bool:
        if not isinstance(world, World):
            return False
        match self.type:
            case "Conjunction":
                left = self.children[0].finalGoalValue(world, mybool)
                right = self.children[1].finalGoalValue(world, mybool)
                mybool = mybool and (world.getValueGoals(left) and world.getValueGoals(right))
            case "Disjunction":
                left = self.children[0].finalGoalValue(world, mybool)
                right = self.children[1].finalGoalValue(world, mybool)
                mybool = mybool and (world.getValueGoals(left) or world.getValueGoals(right))
            case "Parenthesis":
                u = self.children[0].finalGoalValue(world, mybool)
                mybool = mybool and u
            case "Not":
                u = self.children[0].finalGoalValue(world, mybool)
                mybool = mybool and (not u)
            case _:
                for child in self.children:
                    if isinstance(child, Node):
                        mybool = mybool and (child.finalGoalValue(world, mybool))
                    else:
                        mybool = mybool and world.getValueGoals(child)
        return mybool

    def boolValue(self, world: World, mybool: bool) -> bool:
        if not isinstance(world, World):
            return False
        match self.type:
            case "Conjunction":
                left = self.children[0].boolValue(world, mybool)
                right = self.children[1].boolValue(world, mybool)
                mybool = mybool and (world.getValueGoals(left) and world.getValueGoals(right))
            case "Disjunction":
                left = self.children[0].boolValue(world, mybool)
                right = self.children[1].boolValue(world, mybool)
                mybool = mybool and (world.getValueGoals(left) or world.getValueGoals(right))
            case "Parenthesis":
                u = self.children[0].boolValue(world, mybool)
                mybool = mybool and u
            case "Not":
                u = self.children[0].boolValue(world, mybool)
                mybool = mybool and (not u)
            case "Found":
                mybool = mybool and world.isCellWithObject(world.getWillyPosition()[0], self.children[0])
            case "Carrying":
                mybool = mybool and world.isObjectBasket(self.children[0])
            case _:
                for child in self.children:
                    if isinstance(child, Node):
                        mybool = mybool and (child.boolValue(world, mybool))
                    else:
                        mybool = mybool and world.getValueBool(child)
        return mybool

    def timer(self, task: Task) -> None:
        if task.time == "man":
            input('Let us wait for user input (Press Enter to continue)... \n')
            print("###############")
            print(f"State of world '{task.world.id}' after executing task '{task.id}':")
            print(f"Willy Position: {task.world.getWillyPosition()[0]} looking {task.world.getWillyPosition()[1]}")
            print("Basket contents:\n", task.world.getObjectsInBasket())
            print("Final Goal:\n" + task.world.getFinalGoal())
            print("Final Goal Value: ", task.world.getValueFinalGoal())
            print(task.world)
        elif task.time is not None and isinstance(task.time, (int, float)) and task.time > 0:
            print(f'Going to sleep for {task.time} seconds.')
            time.sleep(task.time)
            print("###############")
            print(f"State of world '{task.world.id}' after executing task '{task.id}':")
            print(f"Willy Position: {task.world.getWillyPosition()[0]} looking {task.world.getWillyPosition()[1]}")
            print("Basket contents:\n", task.world.getObjectsInBasket())
            print("Final Goal:\n" + task.world.getFinalGoal())
            print("Final Goal Value: ", task.world.getValueFinalGoal())
            print(task.world)

    def executeMyTask(self, task: Task) -> None:
        if not isinstance(task, Task) or task.fin:
            return

        match self.type:
            case "Drop":
                if task.world.isObjectBasket(self.children[0]) and task.world.isObject(self.children[0]):
                    if not task.dropObject(self.children[0]):
                        print("Cannot drop object:", self.children[0])
                self.timer(task)
            case "Pick":
                if task.world.isCellWithObject(task.world.getWillyPosition()[0], self.children[0]) and task.world.isObject(self.children[0]):
                    if not task.pickObject(self.children[0]):
                        print("Cannot pick object:", self.children[0])
                self.timer(task)
            case "Clear":
                if not task.world.changeBool(self.children[0], False):
                    print("Cannot clear boolean:", self.children[0])
                self.timer(task)
            case "Flip":
                boolAux = task.world.getValueBool(self.children[0])
                if not task.world.changeBool(self.children[0], not boolAux):
                    print("Cannot flip boolean:", self.children[0])
                self.timer(task)
            case "SetBool":
                if not task.world.changeBool(self.children[0], self.children[1]):
                    print("Cannot set boolean:", self.children[0])
                self.timer(task)
            case "SetTrue":
                if not task.world.changeBool(self.children[0], True):
                    print("Cannot set boolean to true:", self.children[0])
                self.timer(task)
            case "Move":
                if not task.moveWilly():
                    print("Willy could not move. Current position:", task.world.getWillyPosition())
                self.timer(task)
            case "TL":
                if not task.turnWilly("left"):
                    print("Cannot turn left")
                self.timer(task)
            case "TR":
                if not task.turnWilly("right"):
                    print("Cannot turn right")
                self.timer(task)
            case "Terminate":
                print("###############")
                print(f"Final state of '{task.world.id}' after executing task '{task.id}' (terminated):")
                print(f"Willy Position: {task.world.getWillyPosition()[0]} looking {task.world.getWillyPosition()[1]}")
                print("Basket contents:\n", task.world.getObjectsInBasket())
                print("Bools state:\n", task.world.getBools())
                print("Final Goal:\n" + task.world.getFinalGoal())
                print("Final Goal Value: ", task.world.getValueFinalGoal())
                print(task.world)
                task.fin = True
                self.timer(task)
            case "ifSimple":
                if self.children[0].boolValue(task.world, True):
                    self.children[1].executeMyTask(task)
                self.timer(task)
            case "ifCompound":
                if self.children[0].boolValue(task.world, True):
                    self.children[1].executeMyTask(task)
                else:
                    self.children[2].executeMyTask(task)
                self.timer(task)
            case "whileInst":
                while self.children[0].boolValue(task.world, True):
                    if task.fin:
                        break
                    self.children[1].executeMyTask(task)
                self.timer(task)
            case "Define As":
                task.instructions.append([self.children[0].children[0], self.children[1]])
                self.timer(task)
            case "Repeat":
                for _ in range(0, self.children[0]):
                    if task.fin:
                        break
                    self.children[1].executeMyTask(task)
                self.timer(task)
            case "MyInstruction":
                if task.instructions:
                    for x in task.instructions:
                        if self.children[0] == x[0]:
                            x[1].executeMyTask(task)
                self.timer(task)
            case _:
                for child in self.children:
                    if isinstance(child, Node):
                        if child.type == "Terminate":
                            child.executeMyTask(task)
                            break
                        else:
                            child.executeMyTask(task)
