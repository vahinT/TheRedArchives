import re

vars = {}

def eval_expr(expr):
    for v in vars:
        expr = expr.replace(v, str(vars[v]))
    return eval(expr)

def run(code):
    lines = [l.strip() for l in code.splitlines() if l.strip()]
    i = 0

    while i < len(lines):
        line = lines[i]

        # PRINT
        if line.startswith("say "):
            print(line[4:].strip('"'))

        # SET
        elif line.startswith("set "):
            name, expr = line[4:].split("=",1)
            vars[name.strip()] = eval_expr(expr.strip())

        # IF
        elif line.startswith("if "):
            cond = line[3:].split("{")[0]
            block = []
            i+=1
            while lines[i] != "}":
                block.append(lines[i])
                i+=1
            if eval_expr(cond):
                run("\n".join(block))

        # WHILE
        elif line.startswith("while "):
            cond = line[6:].split("{")[0]
            block = []
            i+=1
            while lines[i] != "}":
                block.append(lines[i])
                i+=1
            while eval_expr(cond):
                run("\n".join(block))

        # FUNCTION
        elif line.startswith("func "):
            name = line.split("(")[0].split()[1]
            params = line.split("(")[1].split(")")[0].split(",")
            block=[]
            i+=1
            while lines[i] != "}":
                block.append(lines[i])
                i+=1
            vars[name] = ("func",params,block)

        # CALL
        elif "(" in line and ")" in line:
            name = line.split("(")[0]
            args = [eval_expr(a) for a in line.split("(")[1].split(")")[0].split(",")]
            kind, params, block = vars[name]
            old = vars.copy()
            for p,a in zip(params,args):
                vars[p.strip()] = a
            for l in block:
                if l.startswith("return "):
                    val = eval_expr(l[7:])
                    vars.clear()
                    vars.update(old)
                    vars["_return"] = val
                    break
                else:
                    run(l)
        i+=1

def run_file(file):
    with open(file) as f:
        run(f.read())

print("Bix READY.")
