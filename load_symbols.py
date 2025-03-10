import gdb
import pefile
import sys
import mmap
import struct
from elftools.elf.elffile import ELFFile

__all__ = ['LoadSymbols']

integer = type(0xffffffffffffffff)
get_string = lambda value: str(gdb.parse_and_eval(value)) if value.startswith('$') else value
get_number = lambda value: integer(gdb.parse_and_eval(value))
pe_magic = 0x5A4D #MZ


class LoadSymbols(gdb.Command):
    """
    load-symbols <address in loaded PE (e.g. $rip)> <path to PE>
    """

    def __init__(self):
        super(LoadSymbols, self).__init__("load-symbols", gdb.COMMAND_USER)
        self.dont_repeat()

    def invoke(self, args, from_tty):
        argv = gdb.string_to_argv(args)

        # Parse arguments.
        address = get_number(argv[0])
        path = get_string(argv[1])
        print(f'{path}: {address:02x}')

        # Find the base address of the PE.
        base_address = address & 0xfffffffffffff000
        while get_number('*(unsigned short *){}'.format(base_address)) != pe_magic:
            base_address -= 0x1000

        # Print base address.
        print(f'Base ({path}): {base_address:02x}')
        if (base_address == 0x656B000):
            print(get_number('*(unsigned short *){}'.format(base_address)))
            print(pe_magic)


        sections = {}

        # Remove previous symbol file.
        try:
            gdb.execute('remove-symbol-file {path}'.format(path=path))
        except Exception as _error:
            pass

        with open(path, 'rb') as f:
            elffile = ELFFile(f)
            for section in elffile.iter_sections():
                if not section.name:
                    continue
                sections[section.name] = int(section.header["sh_addr"]) + base_address
                #if section.name == ".text" or section.name == ".data":
                #    sections[section.name] = int(section.header["sh_addr"]) + base_address


        # Add the symbol file.
        print('add-symbol-file {path} {textaddr} -s {sections}'.format(
            path=path, textaddr=sections['.text'],
            sections=' -s '.join(
                ' '.join((name, str(address))) for name, address in sections.items() if name != '.text')
        ))
        gdb.execute('add-symbol-file {path} {textaddr} -s {sections}'.format(
            path=path, textaddr=sections['.text'],
            sections=' -s '.join(
                ' '.join((name, str(address))) for name, address in sections.items() if name != '.text')
        ))


LoadSymbols()