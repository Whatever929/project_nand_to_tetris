class Translator(object):
    def __init__(self, file):
        self._sp = 0
        self._local = 1
        self._argument = 2
        self._this = 3
        self._that = 4
        self._temp = 5
        self._pointer = 3
        self._static = 16
        self.file = file
        self.label_generator = self.generate_label()
    def generate_translation(self, vm_code: tuple):
        if vm_code[1] != "":
            if vm_code[0] == "push":
                self.select_data(vm_code[1].partition(" ")[0:3:2])
                self.push_stack()
            elif vm_code[0] == "pop":
                # I think its efficiency can be improved.
                self.save_target_location(vm_code[1].partition(" ")[0:3:2])
                self.pop_stack()
        else:
            if vm_code[0] == "add" or vm_code[0] == "sub":
                self.arithmetic_stack(vm_code[0])
            elif vm_code[0] in ("eq", "gt", "lt"):
                self.comparison_stack(vm_code[0])
            elif vm_code[0] == "neg":
                self.neg_stack()
            else:
                self.logic_stack(vm_code[0])
    def select_data(self, argument:tuple):
        if argument[0] == "constant":
            self.write_file("@{}\nD=A\n".format(argument[1]))
        elif argument[0] == "pointer" or argument[0] == "temp" or argument[0] == "static":
            self.write_file("@{}\nD=A\n@{}\nA=D+A\nD=M\n".format(getattr(self, "_" + argument[0]), argument[1]))
        else:
            self.write_file("@{}\nD=M\n@{}\nA=D+A\nD=M\n".format(getattr(self, "_" + argument[0]), str(argument[1])))
    def push_stack(self):
        self.write_file("@{}\nM=M+1\nA=M-1\nM=D\n".format(self._sp))
    def arithmetic_stack(self, action):
        self.write_file("@{}\nM=M-1\nA=M\nD=M\nA=A-1\nM={}\n".format(self._sp, "D+M" if action == "add" else "M-D"))
    def logic_stack(self, action):
        if action == "not":
            self.write_file("@{}\nA=M-1\nM=!M\n".format(self._sp))
        else:
            self.write_file("@{}\nM=M-1\nA=M\nD=M\nA=A-1\nM={}\n".format(self._sp, "D|M" if action == "or" else "D&M"))
    def neg_stack(self):
        self.write_file("@{}\nA=M-1\nM=-M\n".format(self._sp))
    def save_target_location(self, argument: tuple):
        if argument[0] == "temp" or argument[0] == "pointer" or argument[0] == "static":
            self.write_file("@{}\nD=A\n@{}\nD=D+A\n@{}\nA=M\nM=D\n".format(getattr(self, "_" + argument[0]), argument[1], self._sp))
        else:
            self.write_file("@{}\nD=M\n@{}\nD=D+A\n@{}\nA=M\nM=D\n".format(getattr(self, "_" + argument[0]), argument[1], self._sp))
    def pop_stack(self):
        self.write_file("@{}\nM=M-1\nA=M\nD=M\n@{}\nA=M+1\nA=M\nM=D\n".format(self._sp, self._sp))
    def comparison_stack(self, action):
        new_label = next(self.label_generator)
        asm_to_vm = {"eq": "JEQ", "gt":"JLT", "lt":"JGT"}
        # Compare
        self.write_file("@{}\nM=M-1\nA=M\nD=M\nA=A-1\nD=D-M\n".format(self._sp))
        # Branching implementation
        self.write_file("@CASE_{0}1\nD;{1}\n@CASE_{0}0\n0;JMP\n".format(new_label, asm_to_vm[action]))
        # Details of each branching
        self.write_file("(CASE_{0}0)\n@{1}\nA=M-1\nM=0\n@OUT_{0}\n0;JMP\n".format(new_label, self._sp))
        self.write_file("(CASE_{0}1)\n@{1}\nA=M-1\nM=-1\n@OUT_{0}\n0;JMP\n".format(new_label, self._sp))
        self.write_file("(OUT_{})\n".format(new_label))
    def write_file(self, asm_code):
        with open(self.file, "a") as out:
            out.write(asm_code)
    def generate_label(self):
        count = 0
        while True:
            yield (count:= count + 1)
