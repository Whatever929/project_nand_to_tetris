from parse import parse
from translator import Translator
from sys import argv

with open(argv[1].rstrip(".vm") + ".asm", "w") as f:
    pass
vm_translator = Translator(argv[1].rstrip(".vm") + ".asm")
with open(argv[1]) as f:
    for line in f:
        parsed = parse(line)
        if parsed:
            vm_translator.generate_translation(parsed)
