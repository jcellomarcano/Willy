#!/usr/bin/env python3
"""
CLI Entrypoint for Willy* Interpreter and Simulator.
"""

import sys
import os
import ply.lex as lex
import ply.yacc as yacc

from willy import lexer
from willy import parser
from willy.task import Task
from willy.dashboard import run_interactive_menu

def main():
    args = sys.argv[1:]
    
    filepath = None
    mode = "auto"
    delay = 0.0
    interactive = False
    
    # Process options
    if "-i" in args or "--interactive" in args:
        interactive = True
        # Filter out interactive arguments
        args = [a for a in args if a not in ("-i", "--interactive")]
        
    if len(args) == 0:
        try:
            filepath = input('File to interpret: ').strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)
    elif len(args) >= 1:
        filepath = args[0]
        
        if len(args) >= 2:
            opt = args[1]
            if opt in ("-m", "--manual"):
                mode = "manual"
                delay = "man"
            elif opt in ("-a", "--auto"):
                mode = "auto"
                if len(args) >= 3:
                    try:
                        delay = float(args[2])
                        if delay < 0:
                            print("The amount in seconds must be an integer or decimal greater than or equal to 0", file=sys.stderr)
                            sys.exit(1)
                    except ValueError:
                        print("The amount in seconds must be an integer or decimal greater than or equal to 0", file=sys.stderr)
                        sys.exit(1)
                else:
                    delay = 0.0
            else:
                print("Usage: willy <filename> <--manual|-m>")
                print("Usage: willy <filename> <--auto|-a> <float representing seconds>\n")
                sys.exit(1)

    if not filepath:
        print("Error: No input file specified.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Unable to open file {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)

    # Reset module-level errors
    parser.ParserErrors.clear()
    lexer.InvalidTokens.clear()
    
    if interactive:
        Task.add_element("dashboard")
    else:
        Task.add_element(delay)

    # Initialize parser and lexer
    try:
        lex_instance = lex.lex(module=lexer)
        yacc_instance = yacc.yacc(module=parser, debug=False, write_tables=False)
    except Exception as e:
        print(f"Failed to initialize parser/lexer: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse and run
    try:
        parser.tasks.clear()
        parser.createdWorlds.clear()
        parser.programBlock.clear()
        
        ast_root = yacc_instance.parse(content, lexer=lex_instance)
        
        if len(lexer.InvalidTokens) > 0:
            print(lexer.InvalidTokens[0])
            sys.exit(1)
            
        if len(parser.ParserErrors) > 0:
            print(parser.ParserErrors[0])
            sys.exit(1)
            
        if not ast_root:
            print("Syntax error at EOF", file=sys.stderr)
            sys.exit(1)
            
        if interactive:
            run_interactive_menu(ast_root, parser.tasks)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error during execution: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
