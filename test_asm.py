from asm import disassemble, assemble, lex

prog = [0x7c01, 0x0030, 0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d,
        0x7dc1, 0x001a, 0xa861, 0x7c01, 0x2000, 0x2161, 0x2000, 0x8463,
        0x806d, 0x7dc1, 0x000d, 0x9031, 0x7c10, 0x0018, 0x7dc1, 0x001a,
        0x9037, 0x61c1, 0x7dc1, 0x001a, 0x0000, 0x0000, 0x0000, 0x0000]

asm = '''SET A, 0x30
SET [0x1000], 0x20
SUB A, [0x1000]
IFN A, 0x10
SET PC, 0x1a
SET I, 0xa
SET A, 0x2000
SET [0x2000+I], [A]
SUB I, 0x1
IFN I, 0x0
SET PC, 0xd
SET X, 0x4
JSR 0x18
SET PC, 0x1a
SHL X, 0x4
SET PC, POP
SET PC, 0x1a'''


def test_disassemble():
    assert disassemble(prog) == asm


def test_assemble_one():
    assert lex('SET X, 2') == [['SET', 'X', ',', '2']]


def test_assemble_comment():
    assert lex('SET X, 2 ; foo') == lex('SET X, 2 ; foo')


def test_assemble_disassembled():
    assert assemble(asm) == prog


def test_assemble_example():
    with open('example.s') as f:
        example = f.read()

    assert assemble(example) == prog
