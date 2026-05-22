#!/usr/bin/env python3
"""
Dashboard and Visualization Utilities for Willy* AST.
Provides AST pretty-printing, metrics collection, and interactive prompt.
"""

import sys
from willy.node import Node
from willy.lca import LCASolver

def render_ascii_tree(node, prefix="", is_last=True):
    if not isinstance(node, Node):
        return ""
    
    # Format node details
    idx_str = f"\033[93m[{node.index}]\033[0m " if node.index is not None else ""
    node_type = f"\033[96m{node.type}\033[0m"
    
    # Handle non-node children (like constants or names)
    non_node_children = [c for c in node.children if not isinstance(c, Node)]
    val_str = ""
    if non_node_children:
        val_str = f" (\033[92m{', '.join(map(str, non_node_children))}\033[0m)"
        
    line = f"{prefix}{'└── ' if is_last else '├── '}{idx_str}{node_type}{val_str}\n"
    
    # Recursively render Node children
    node_children = [c for c in node.children if isinstance(c, Node)]
    new_prefix = prefix + ("    " if is_last else "│   ")
    
    for i, child in enumerate(node_children):
        line += render_ascii_tree(child, new_prefix, i == len(node_children) - 1)
        
    return line

def pretty_print_tree(node: Node) -> str:
    """Returns a colored ASCII tree representation of the AST."""
    if not isinstance(node, Node):
        return str(node)
        
    idx_str = f"\033[93m[{node.index}]\033[0m " if node.index is not None else ""
    node_type = f"\033[96m{node.type}\033[0m"
    non_node_children = [c for c in node.children if not isinstance(c, Node)]
    val_str = ""
    if non_node_children:
        val_str = f" (\033[92m{', '.join(map(str, non_node_children))}\033[0m)"
        
    header = f"{idx_str}{node_type}{val_str}\n"
    node_children = [c for c in node.children if isinstance(c, Node)]
    
    body = ""
    for i, child in enumerate(node_children):
        body += render_ascii_tree(child, "", i == len(node_children) - 1)
        
    return header + body

def collect_metrics(node: Node) -> dict:
    """Traverses the AST to collect structure and complexity statistics."""
    metrics = {
        "total_nodes": 0,
        "max_depth": 0,
        "primitive_commands": 0,
        "control_structures": 0,
        "logical_conditions": 0,
        "procedures_defined": 0,
    }
    
    def traverse(n, depth):
        if not isinstance(n, Node):
            return
        
        metrics["total_nodes"] += 1
        metrics["max_depth"] = max(metrics["max_depth"], depth)
        
        t = n.type
        if t in ("Move", "TL", "TR", "Pick", "Drop", "SetBool", "SetTrue", "Clear", "Flip", "Terminate"):
            metrics["primitive_commands"] += 1
        elif t in ("ifSimple", "ifCompound", "whileInst", "Repeat"):
            metrics["control_structures"] += 1
        elif t in ("Conjunction", "Disjunction", "Not", "Parenthesis", "Found", "Carrying"):
            metrics["logical_conditions"] += 1
        elif t == "Define As":
            metrics["procedures_defined"] += 1
            
        for child in n.children:
            if isinstance(child, Node):
                traverse(child, depth + 1)
                
    traverse(node, 1)
    return metrics

def run_interactive_menu(root: Node, task_instances: list):
    """Launches the interactive ASCII CLI Dashboard."""
    # Assign indices to all AST Nodes
    root.assign_indices(1)
    
    # Initialize LCA solver
    lca_solver = LCASolver(root)
    
    print("\033[95m==========================================================")
    print("        WILLY* INTERACTIVE AST & SIMULATOR DASHBOARD      ")
    print("==========================================================\033[0m")
    
    while True:
        print("\n\033[1mSelect an option:\033[0m")
        print("  1. View AST Statistics & Complexity Metrics")
        print("  2. Display Colored ASCII Tree Layout (with Node IDs)")
        print("  3. Query Lowest Common Ancestor (LCA) & Divergence Path")
        print("  4. Execute Program Tasks Simulation")
        print("  5. Exit Dashboard")
        
        try:
            choice = input("\nEnter choice (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting dashboard.")
            break
            
        if choice == "1":
            metrics = collect_metrics(root)
            print("\n\033[92m--- AST Complexity Metrics ---")
            print(f"  Total AST Nodes:         {metrics['total_nodes']}")
            print(f"  Max AST Depth:           {metrics['max_depth']}")
            print(f"  Primitive Commands:      {metrics['primitive_commands']}")
            print(f"  Control Structures:      {metrics['control_structures']}")
            print(f"  Logical Conditions:      {metrics['logical_conditions']}")
            print(f"  Custom Procedures:       {metrics['procedures_defined']}")
            print("------------------------------\033[0m")
            
        elif choice == "2":
            print("\n\033[92m--- AST Graphical Layout ---\033[0m")
            print(pretty_print_tree(root))
            print("\033[92m----------------------------\033[0m")
            
        elif choice == "3":
            print("\n\033[94m--- LCA Query Tool ---")
            try:
                id1_str = input("  Enter Node ID 1: ").strip()
                id2_str = input("  Enter Node ID 2: ").strip()
                id1 = int(id1_str)
                id2 = int(id2_str)
            except ValueError:
                print("  \033[91mError: Node IDs must be integers.\033[0m")
                continue
                
            lca_node, explanation = lca_solver.find_lca(id1, id2)
            if lca_node:
                print(f"\n  \033[93m[LCA Node Found]\033[0m")
                print(f"    Node ID:      {lca_node.index}")
                print(f"    Node Type:    {lca_node.type}")
                print(f"    Explanation:  {explanation}")
            else:
                print(f"\n  \033[91mQuery failed: {explanation}\033[0m")
            print("\033[94m----------------------\033[0m")
            
        elif choice == "4":
            print("\n\033[95m--- Task Simulation ---\033[0m")
            if not task_instances:
                print("  No tasks defined in this program.")
                continue
                
            print("  Available Tasks:")
            for idx, task in enumerate(task_instances):
                print(f"    {idx + 1}. Task '{task.id}' on World '{task.world.id}'")
            
            try:
                task_choice = input(f"  Select task to run (1-{len(task_instances)}) or 'all': ").strip()
            except (KeyboardInterrupt, EOFError):
                continue
                
            tasks_to_run = []
            if task_choice.lower() == "all":
                tasks_to_run = task_instances
            else:
                try:
                    t_idx = int(task_choice) - 1
                    if 0 <= t_idx < len(task_instances):
                        tasks_to_run = [task_instances[t_idx]]
                    else:
                        print("  \033[91mInvalid task selection.\033[0m")
                        continue
                except ValueError:
                    print("  \033[91mInvalid input.\033[0m")
                    continue
            
            # Select run mode
            print("\n  Simulation Execution Mode:")
            print("    a) Automatic (runs to completion)")
            print("    m) Manual (step-by-step with Enter keys)")
            mode = input("  Select mode (a/m): ").strip().lower()
            
            time_val = "man" if mode == "m" else 0
            
            for t in tasks_to_run:
                # Reset task state to execute cleanly
                t.fin = False
                t.time = time_val
                print(f"\n\033[93m>>> Starting Execution of Task '{t.id}' on World '{t.world.id}' <<<\033[0m")
                # Locate the specific task AST Node and execute it
                # We can find the task block in the tree. Or since we just want to run the task,
                # we can find the AST representation of task block if available,
                # or just run it via the simulation instance logic.
                # In parser.py: `p[0].executeMyTask(currentTask)` runs the simulation.
                # The simulation logic for a task `t` is defined by executing its task AST block.
                # Let's search the root children for the Task node that matches the task id.
                task_node = None
                
                # Helper to find Task node in program block
                def find_task_node(n):
                    if not isinstance(n, Node):
                        return None
                    if n.type == "Task" and len(n.children) > 0 and n.children[0].children[0] == t.id:
                        return n
                    for child in n.children:
                        res = find_task_node(child)
                        if res:
                            return res
                    return None
                
                task_node = find_task_node(root)
                if task_node:
                    # Run the instructions child of the Task node
                    # In taskBlock, children are: [taskDefinition, multiInstructions]
                    if len(task_node.children) > 1:
                        task_node.children[1].executeMyTask(t)
                        
                        # Print final result
                        print("\033[92m==========================================================")
                        print(f"Simulation of Task '{t.id}' finished successfully!")
                        print(f"Willy final position: {t.world.getWillyPosition()[0]} looking {t.world.getWillyPosition()[1]}")
                        print("Basket contents:\n", t.world.getObjectsInBasket())
                        print("Bools state:\n", t.world.getBools())
                        print("Final Goal:\n" + t.world.getFinalGoal())
                        print("Final Goal Value: ", t.world.getValueFinalGoal())
                        print(t.world)
                        print("==========================================================\033[0m")
                else:
                    print(f"  \033[91mCould not locate AST Node for task '{t.id}'.\033[0m")
            
        elif choice == "5":
            print("Exiting dashboard. Goodbye!")
            break
        else:
            print("  \033[91mInvalid choice. Please enter a number between 1 and 5.\033[0m")
