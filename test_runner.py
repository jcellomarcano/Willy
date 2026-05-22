#!/usr/bin/env python3
"""
Test Runner for Willy* Interpreter.
Runs all tests inside tests/ directory and prints status reports.
"""

import os
import subprocess
import sys

def main():
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    if not os.path.isdir(test_dir):
        print(f"Error: tests directory not found at {test_dir}", file=sys.stderr)
        sys.exit(1)

    test_files = sorted([f for f in os.listdir(test_dir) if f.endswith(".txt")])
    if not test_files:
        print("No test files found in tests directory.", file=sys.stderr)
        sys.exit(0)

    print("\033[95m==========================================================")
    print("                WILLY* TEST RUNNER SUITE                  ")
    print("==========================================================\033[0m\n")

    passed_files = 0
    failed_files = 0
    total_tasks = 0
    successful_tasks = 0

    results = []

    for file_name in test_files:
        file_path = os.path.join(test_dir, file_name)
        
        # Run CLI with auto mode and 0 delay
        cmd = [sys.executable, "-m", "willy.cli", file_path, "-a", "0"]
        
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            results.append((file_name, "TIMEOUT", []))
            failed_files += 1
            continue

        if res.returncode != 0:
            err_msg = res.stderr.strip() or res.stdout.strip() or "Unknown error"
            results.append((file_name, "FAILED (Exit Code)", [("Compilation/Execution", False, err_msg)]))
            failed_files += 1
            continue

        # Parse task output to see if goals were achieved
        stdout_lines = res.stdout.splitlines()
        tasks_info = []
        
        current_task = None
        for line in stdout_lines:
            if "Final state of world" in line and "after executing task" in line:
                # Extract task name
                parts = line.split("after executing task")
                if len(parts) > 1:
                    current_task = parts[1].replace("'", "").replace(":", "").strip()
            elif "Final Goal Value:" in line:
                val = "True" in line
                if current_task:
                    tasks_info.append((current_task, val, ""))
                    current_task = None

        if not tasks_info:
            # If no tasks ran, check if the file was just a world definition without tasks
            if "Initial state of" in res.stdout:
                results.append((file_name, "PASSED (World only)", []))
                passed_files += 1
            else:
                results.append((file_name, "PASSED (No Output)", []))
                passed_files += 1
        else:
            results.append((file_name, "PASSED", tasks_info))
            passed_files += 1
            total_tasks += len(tasks_info)
            successful_tasks += sum(1 for t in tasks_info if t[1])

    # Print Report Table
    print(f"{'Test File':<35} | {'Status':<15} | {'Tasks Summary'}")
    print("-" * 80)
    for file_name, status, tasks in results:
        status_color = "\033[92m" if "PASSED" in status else "\033[91m"
        print(f"{file_name:<35} | {status_color}{status:<15}\033[0m | ", end="")
        if not tasks:
            print("No tasks ran.")
        else:
            task_summaries = []
            for t_name, success, err in tasks:
                t_color = "\033[92m" if success else "\033[93m"
                task_summaries.append(f"{t_name}({t_color}{'Achieved' if success else 'Unachieved'}\033[0m)")
            print(", ".join(task_summaries))

    print("\n\033[95m==========================================================")
    print("                    EXECUTION SUMMARY                     ")
    print("==========================================================\033[0m")
    print(f"  Total Test Files Processed:  {len(test_files)}")
    print(f"  Passed Files:                \033[92m{passed_files}\033[0m")
    print(f"  Failed Files:                \033[91m{failed_files}\033[0m")
    if total_tasks > 0:
        print(f"  Total Tasks Executed:        {total_tasks}")
        print(f"  Tasks Achieving Final Goal:  {successful_tasks} ({successful_tasks/total_tasks*100:.1f}%)")
    print("\033[95m==========================================================\033[0m")

    if failed_files > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
