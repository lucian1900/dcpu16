import re

comment_pattern = re.compile(r';.*\n')

basic_op = ['SET', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'SHL', 'SHR', 'AND',
            'BOR', 'XOR', 'IFE', 'IFN', 'IFG', 'IFB']

reg_names = ['A', 'B', 'C', 'X', 'Y', 'Z', 'I', 'J']


def disassemble(code):
    'Ported from https://gist.github.com/2300590'

    PC = [0]

    def operand(bits):

        if bits <= 0x07:
            return reg_names[bits]

        if bits <= 0x0f:
            return '[{0}]'.format(reg_names[bits - 0x08])

        if bits <= 0x17:
            PC[0] += 1
            return '[{0}+{1}]'.format(hex(code[PC[0]]), reg_names[bits - 0x10])

        if bits == 0x18:
            return 'POP'

        if bits == 0x19:
            return 'PEEK'

        if bits == 0x1a:
            return 'PUSH'

        if bits == 0x1b:
            return 'SP'

        if bits == 0x1c:
            return 'PC'

        if bits == 0x1d:
            return 'O'

        if bits == 0x1e:
            PC[0] += 1
            return '[{0}]'.format(hex(code[PC[0]]))

        if bits == 0x1f:
            # literal
            PC[0] += 1
            return hex(code[PC[0]])

        # literal
        return hex(bits - 0x20)

    asm = []

    while PC[0] < len(code):
        inst = code[PC[0]]

        if inst & 0xf == 0:
            # non-basic
            if ((inst >> 4) & 0x3f) == 0x01:
                asm.append('JSR ' + operand(inst >> 10))
        else:
                asm.append('{0} {1}, {2}'.format(basic_op[inst & 0xf - 1],
                                                 operand((inst >> 4) & 0x3f),
                                                 operand(inst >> 10)))

        PC[0] += 1

    return '\n'.join(asm)


def assemble(source):
    insts = lex(source)
    binary = []

    labels = {}
    for i, inst in enumerate(insts):
        if inst[0] == ':':
            if isinstance(inst, str):
                labels[inst[1]] = i
                insts[i] = insts[2:]
            else:
                raise SyntaxError("Expected string label, got: {0}" \
                                    .format(inst))

    ops = dict((e, i + 1) for i, e in enumerate(basic_op))

    for i, inst in enumerate(insts):
        if inst[0] not in ops:
            # non-basic op
            low = 0x0
            mid = 0x01 << 4
        else:
            # basic op
            low = ops[inst[0]]
            mid = 0x0 << 4  # TODO hadle value a

        high = 0x0 << 10 # TODO handle value b

        binary.append(low + mid + high)

    return binary


def lex(source):
    source = re.sub(comment_pattern, ' ', source)

    lines = source.split('\n')
    separators = [':', ',', '[', ']', '++', '--', '+', '-']

    for i, _ in enumerate(lines):
        for s in separators:
            lines[i] = lines[i].replace(s, ' {0} '.format(s))

        lines[i] = lines[i].split()

    return lines


if __name__ == '__main__':
    prog = [
        0x7c01, 0x0030, 0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d,
        0x7dc1, 0x001a, 0xa861, 0x7c01, 0x2000, 0x2161, 0x2000, 0x8463,
        0x806d, 0x7dc1, 0x000d, 0x9031, 0x7c10, 0x0018, 0x7dc1, 0x001a,
        0x9037, 0x61c1, 0x7dc1, 0x001a, 0x0000, 0x0000, 0x0000, 0x0000]

    asm = disassemble(prog)
    print asm

    print assemble(asm)

    print assemble(":foo SET PC 0x01")
