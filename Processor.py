from registerFiles import registerfiles
from register_table import register_table
from machineCode_parser import machineCode_parser
import sys
try:
    print('Pprogram running...')

    file_in = open('Machine_code.txt')
    instructions = []
    for line in file_in:
        line = line.strip()
        instructions.append(line)
    parse_instructions = machineCode_parser(registerfiles,register_table)
    parse_instructions.parse(instructions)
    sys.exit(0)

except Exception as e:
    print(f'Program failed: {e}')
    sys.exit(1)
