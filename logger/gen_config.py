import sys

with open("config.py.template") as f:
    template = f.read()

if __name__ == '__main__':
    for i in sys.argv[1:]:
        template += f"TASKS += [{i}]\n"
    with open("config.py", "w") as f:
        f.write(template)
