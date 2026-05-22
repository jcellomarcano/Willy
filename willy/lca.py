#!/usr/bin/env python3
"""
Lowest Common Ancestor (LCA) Solver and Caching logic for Willy* AST.
"""

from willy.node import Node

class LCASolver:
    def __init__(self, root: Node | None):
        self.root = root
        self.paths: dict[int, list[Node]] = {}  # index -> list of Node objects from root to node
        self.lca_cache: dict[tuple[int, int], tuple[Node | None, str]] = {}  # (index1, index2) -> (lca_node, explanation)
        self.build_cache()

    def _dfs_paths(self, node: Node | None, current_path: list[Node]):
        if not isinstance(node, Node):
            return
        
        # Append copy of current path plus the node itself
        path_to_node = current_path + [node]
        if node.index is not None:
            self.paths[node.index] = path_to_node
        
        for child in node.children:
            if isinstance(child, Node):
                self._dfs_paths(child, path_to_node)

    def build_cache(self):
        """Builds the paths cache from the root node using DFS."""
        if self.root:
            self._dfs_paths(self.root, [])

    def find_lca(self, index1: int, index2: int) -> tuple[Node | None, str]:
        """
        Finds the LCA of two nodes by their indices.
        Returns a tuple of (lca_node, explanation).
        """
        # Ensure indices are sorted for uniform caching key
        key = (min(index1, index2), max(index1, index2))
        if key in self.lca_cache:
            return self.lca_cache[key]

        if index1 not in self.paths or index2 not in self.paths:
            return None, "One or both node indices do not exist in the AST."

        path1 = self.paths[index1]
        path2 = self.paths[index2]

        lca_node = None
        min_len = min(len(path1), len(path2))
        
        # Find the last common node in both paths
        for i in range(min_len):
            if path1[i].index == path2[i].index:
                lca_node = path1[i]
            else:
                break

        if not lca_node:
            return None, "No common ancestor found (detached trees)."

        # Determine divergence reason
        explanation = self._explain_divergence(lca_node, path1, path2)
        self.lca_cache[key] = (lca_node, explanation)
        return lca_node, explanation

    def _explain_divergence(self, lca_node: Node, path1: list[Node], path2: list[Node]) -> str:
        """
        Explains why and where the path to the two nodes diverged.
        """
        if path1[-1].index == path2[-1].index:
            return f"Nodes are the same node (Index {path1[-1].index}) of type '{lca_node.type}'."

        # Find the child nodes of the LCA through which the paths branch
        child1 = None
        child2 = None
        
        lca_idx_in_p1 = path1.index(lca_node)
        lca_idx_in_p2 = path2.index(lca_node)

        if lca_idx_in_p1 + 1 < len(path1):
            child1 = path1[lca_idx_in_p1 + 1]
        if lca_idx_in_p2 + 1 < len(path2):
            child2 = path2[lca_idx_in_p2 + 1]

        match lca_node.type:
            case "Program Block:" | "MultiInstruction" | "Instructions" | "Begin":
                return (f"Sequential execution divergence inside '{lca_node.type}' block. "
                        f"Node {path1[-1].index} is executed within branch/statement '{child1.type if child1 else 'None'}', "
                        f"while Node {path2[-1].index} is executed in branch/statement '{child2.type if child2 else 'None'}'.")
            
            case "ifCompound":
                idx1 = lca_node.children.index(child1) if child1 in lca_node.children else -1
                idx2 = lca_node.children.index(child2) if child2 in lca_node.children else -1
                
                parts = {0: "Condition", 1: "Then-branch", 2: "Else-branch"}
                part1 = parts.get(idx1, "Unknown-part")
                part2 = parts.get(idx2, "Unknown-part")
                
                return (f"Conditional divergence inside 'if-then-else' block (Node {lca_node.index}). "
                        f"Node {path1[-1].index} is under the {part1}, "
                        f"and Node {path2[-1].index} is under the {part2}.")

            case "ifSimple":
                idx1 = lca_node.children.index(child1) if child1 in lca_node.children else -1
                idx2 = lca_node.children.index(child2) if child2 in lca_node.children else -1
                
                parts = {0: "Condition", 1: "Then-branch"}
                part1 = parts.get(idx1, "Unknown-part")
                part2 = parts.get(idx2, "Unknown-part")
                
                return (f"Conditional divergence inside 'if-then' block (Node {lca_node.index}). "
                        f"Node {path1[-1].index} is under the {part1}, "
                        f"and Node {path2[-1].index} is under the {part2}.")

            case "whileInst":
                idx1 = lca_node.children.index(child1) if child1 in lca_node.children else -1
                idx2 = lca_node.children.index(child2) if child2 in lca_node.children else -1
                
                parts = {0: "Loop Condition", 1: "Loop Body"}
                part1 = parts.get(idx1, "Unknown-part")
                part2 = parts.get(idx2, "Unknown-part")
                
                return (f"Loop control divergence inside 'while' statement (Node {lca_node.index}). "
                        f"Node {path1[-1].index} is under the {part1}, "
                        f"and Node {path2[-1].index} is under the {part2}.")

            case "Repeat":
                return (f"Loop body divergence inside 'repeat' statement (Node {lca_node.index}). "
                        f"They diverged inside the repeated block execution.")

            case "Define As":
                return (f"Divergence inside custom procedure definition '{lca_node.children[0].type if len(lca_node.children) > 0 else ''}' (Node {lca_node.index}).")

            case _:
                return (f"Divergence at Node {lca_node.index} of type '{lca_node.type}'. "
                        f"Paths parted into sub-nodes '{child1.type if child1 else 'None'}' and '{child2.type if child2 else 'None'}'.")
