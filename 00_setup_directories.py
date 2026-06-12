import os

project_path = os.path.dirname(os.path.abspath(__file__))

folders = [
    "Assets",
    os.path.join("Assets", "Shapes"),
    os.path.join("Assets", "Results"),
    os.path.join("Assets", "Tables"),
    "Figures",
]

for folder in folders:
    os.makedirs(os.path.join(project_path, folder), exist_ok=True)
