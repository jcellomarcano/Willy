#!/usr/bin/env python3

"""
    ModelProcedure helper class to search lists of symbols or objects.
"""

class ModelProcedure:
    def __init__(self):
        self.symbol = []

    def find_obj(self, symbol, array):
        # Search for a symbol key in a list of [key, data] pairs
        for element in array:
            if element[0] == symbol:
                return True
        return False

    def find(self, symbol, array):
        # Search for an object by its id attribute in a list of objects
        for element in array:
            if element.id == symbol:
                return element
        return None
