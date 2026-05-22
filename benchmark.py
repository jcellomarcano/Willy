#!/usr/bin/env python3
import time
import random
from willy.node import Node
from willy.lca import LCASolver

def generate_balanced_tree(depth, node_type="Node"):
    if depth <= 0:
        return Node(node_type)
    left_child = generate_balanced_tree(depth - 1, node_type)
    right_child = generate_balanced_tree(depth - 1, node_type)
    return Node(node_type, [left_child, right_child])

def recursive_lca(root, idx1, idx2):
    if root is None:
        return None
    if root.index == idx1 or root.index == idx2:
        return root
    
    found_left = None
    found_right = None
    
    if len(root.children) > 0 and isinstance(root.children[0], Node):
        found_left = recursive_lca(root.children[0], idx1, idx2)
    if len(root.children) > 1 and isinstance(root.children[1], Node):
        found_right = recursive_lca(root.children[1], idx1, idx2)
        
    if found_left is not None and found_right is not None:
        return root
    return found_left if found_left is not None else found_right

def main():
    print("======================================================================")
    print("                   WILLY* AST LCA BENCHMARK SUITE                     ")
    print("======================================================================")
    print(f"{'Depth':<6} | {'Num Nodes':<9} | {'Queries':<8} | {'Recursive (s)':<14} | {'Cached LCA (s)':<14} | {'Speedup':<8}")
    print("-" * 78)
    
    for depth in range(6, 13):
        # 1. Generate Tree
        root = generate_balanced_tree(depth)
        num_nodes = root.assign_indices(1) - 1
        
        # 2. Setup Queries
        num_queries = 2000
        query_pairs = []
        for _ in range(num_queries):
            id1 = random.randint(1, num_nodes)
            id2 = random.randint(1, num_nodes)
            query_pairs.append((id1, id2))
            
        # 3. Benchmark Recursive LCA
        start_rec = time.perf_counter()
        for idx1, idx2 in query_pairs:
            recursive_lca(root, idx1, idx2)
        end_rec = time.perf_counter()
        time_rec = end_rec - start_rec
        
        # 4. Benchmark Cached LCA (includes build time + query time)
        start_cache = time.perf_counter()
        solver = LCASolver(root)
        for idx1, idx2 in query_pairs:
            solver.find_lca(idx1, idx2)
        end_cache = time.perf_counter()
        time_cache = end_cache - start_cache
        
        speedup = time_rec / time_cache if time_cache > 0 else float('inf')
        
        print(f"{depth:<6} | {num_nodes:<9} | {num_queries:<8} | {time_rec:<14.6f} | {time_cache:<14.6f} | {speedup:<8.2f}x")
        
    print("======================================================================")

if __name__ == "__main__":
    main()
