#!/usr/bin/env python3
import sys

"""
    Stack structure for interpreter symbol table verification.
    Manages scopes (global, world, task, and nested custom instructions).
"""

class Stack:
    def __init__(self):
        # Initialize stack with a dictionary representing the global scope
        self.stack = [{}]
        self.level = 1

    def find(self, symbol):
        """Checks if a symbol exists in the current active scope (top of the stack)."""
        if not self.stack:
            return False
        return symbol in self.stack[-1]

    def insert(self, symbol, data):
        """Inserts a symbol into the current active scope, failing if it already exists."""
        if not self.find(symbol):
            self.stack[-1][symbol] = data
        else:
            print(f"Semantic error: The element '{symbol}' already exists in this scope and cannot be added again.", file=sys.stderr)
            sys.exit(1)

    def push(self, table=None):
        """Pushes a new scope level on the stack."""
        if table is None or not isinstance(table, dict):
            table = {}
        self.stack.append(table)
        self.level = len(self.stack)

    def pop(self):
        """Pops the current active scope, returning to the parent scope."""
        if len(self.stack) > 1:
            self.stack.pop()
            self.level = len(self.stack)
            return True
        return False

    def push_empty_table(self):
        """Alias for push to match legacy naming conventions."""
        self.push({})

    def empty(self):
        return len(self.stack) == 0

    def __str__(self):
        return str(self.stack)
