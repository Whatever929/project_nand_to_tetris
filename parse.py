def parse(line):
    if line[0:2] == "//" or line.strip() == "":
        return False
    else:
        return line.strip().partition(" ")[0:3:2]
