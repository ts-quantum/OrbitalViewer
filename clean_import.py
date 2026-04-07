import os
import ast

def analyze_imports(directory):
    print(f"{'DATEI':<30} | {'IMPORT-TYP':<15} | {'MODULE'}")
    print("-" * 80)
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != __file__:
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            # Normaler Import: import os, sympy
                            if isinstance(node, ast.Import):
                                names = [n.name for n in node.names]
                                print(f"{file:<30} | Standard      | {', '.join(names)}")
                            
                            # From-Import: from sympy import exp
                            elif isinstance(node, ast.ImportFrom):
                                module = node.module or "Relative"
                                names = [n.name for n in node.names]
                                if "*" in names:
                                    print(f"\033[91m{file:<30} | WILDCARD (*)  | from {module} import *\033[0m")
                                else:
                                    print(f"{file:<30} | From-Import   | from {module} import {', '.join(names)}")
                    except Exception as e:
                        print(f"Fehler in {file}: {e}")

if __name__ == "__main__":
    # Scanne den aktuellen Ordner
    analyze_imports(".")

