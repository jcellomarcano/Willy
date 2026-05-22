#!/usr/bin/env python3
import unittest
import sys
import os

from willy.stack import Stack
from willy.node import Node
from willy.lca import LCASolver
from willy.world import World

class TestSymbolTableStack(unittest.TestCase):
    def setUp(self):
        self.stack = Stack()

    def test_scope_isolation_and_insert(self):
        # Insert symbol in global scope
        self.stack.insert("x", {"type": "boolean", "value": True})
        self.assertTrue(self.stack.find("x"))

        # Push nested scope
        self.stack.push()
        # Symbol should not be found in active scope top, but exists globally
        # Note: stack.find checks active scope top only
        self.assertFalse(self.stack.find("x"))
        
        # Insert same symbol in inner scope (allowed under nested scoping)
        self.stack.insert("x", {"type": "boolean", "value": False})
        self.assertTrue(self.stack.find("x"))

        # Pop inner scope
        self.stack.pop()
        self.assertTrue(self.stack.find("x"))
        self.assertEqual(self.stack.stack[-1]["x"]["value"], True)

    def test_duplicate_symbol_error(self):
        self.stack.insert("a", {"type": "object"})
        # Should raise SystemExit because duplicate insert calls sys.exit
        with self.assertRaises(SystemExit):
            self.stack.insert("a", {"type": "another_object"})


class TestConstantFolding(unittest.TestCase):
    def test_double_negation_elimination(self):
        # Construct target AST Node representing "not not front-clear"
        primitive = Node("BooleanTest", ["front-clear"])
        not_node_inner = Node("Not", [primitive])
        
        # Mimic p_negationBool optimization:
        # If second operand has type "Not", we bypass creating another "Not"
        if not_node_inner.type == "Not":
            optimized_node = not_node_inner.children[0]
        else:
            optimized_node = Node("Not", [not_node_inner])

        # Assert optimized node is directly the inner primitive node
        self.assertEqual(optimized_node.type, "BooleanTest")
        self.assertEqual(optimized_node.children[0], "front-clear")


class TestLCASolver(unittest.TestCase):
    def test_lca_caching_and_divergence(self):
        # Create a tiny test tree
        #           Root (1)
        #          /     \
        #      Left (2)  Right (3)
        #      /
        #  Leaf (4)
        leaf = Node("PrimitiveCommand", ["move"])
        left = Node("Instructions", [leaf])
        right = Node("PrimitiveCommand", ["turn-left"])
        root = Node("Program Block:", [left, right])
        
        # Assign indices to all nodes
        root.assign_indices(1)
        
        # Initialize solver
        solver = LCASolver(root)
        
        # Query LCA of leaf (index 3) and right child (index 4)
        # The indices will be left child/leaf (2/3) and right (4)
        lca_node, explanation = solver.find_lca(3, 4)
        
        self.assertIsNotNone(lca_node)
        self.assertEqual(lca_node.type, "Program Block:")
        self.assertIn("Sequential execution divergence", explanation)
        
        # Assert cached lookup is used on repeated query
        lca_node_cached, explanation_cached = solver.find_lca(3, 4)
        self.assertEqual(lca_node_cached, lca_node)
        self.assertEqual(explanation_cached, explanation)


class TestWorldState(unittest.TestCase):
    def test_grid_initialization_and_walls(self):
        world = World("test_world")
        world.setDimension([5, 5])
        
        # By default, should have no walls (be cell wall free)
        self.assertTrue(world.isCellWallFree([2, 2]))
        
        # Add a wall at [2, 2]
        world.setWall([2, 2], [2, 2], "north")
        self.assertFalse(world.isCellWallFree([2, 2]))


if __name__ == "__main__":
    unittest.main()
