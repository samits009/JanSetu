import ast
import os

def find_imports(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for n in node.names:
                                    if 'app.db.session' in n.name:
                                        print(f"{path}: import {n.name}")
                            elif isinstance(node, ast.ImportFrom):
                                if node.module and 'app.db.session' in node.module:
                                    print(f"{path}: from {node.module} import ...")
                    except Exception as e:
                        pass
find_imports('tests')
