import os
import gdb
from string import printable

def read_until(pipe, substring):
    lines = b''
    while True:
        l = pipe.read(1)
        if l:
            lines += l
            if substring in lines:
                break
    return lines

def emtpy_pipe(pipe):
    while True:
        c = pipe.read(1)
        if len(c) == 0:
            return

def read_and_print(pipe):
    old_blocking = os.get_blocking(pipe.fileno())
    os.set_blocking(pipe.fileno(), True)
    while True:
        c = pipe.read(1).decode('ascii')
        if c in printable:
            print(c, end='')

def read_line(pipe):
    os.set_blocking(pipe.fileno(), True)
    line = pipe.readline().decode('ascii')
    print(line)
    return line

INPUT_PIPE = '/tmp/guest.in'
OUTPUT_PIPE = '/tmp/guest.out'
ADD_SYMBOL_FILE_STR = b'Image base:\n'

print("Connecting to qemu...")
if gdb.selected_inferior().connection:
    gdb.execute('disconnect')

gdb.execute('target remote localhost:1234')
print("gdb connected to localhost:1234")
gdb.execute('c&')
print("gdb continued...")

try:
    input_handle = open(INPUT_PIPE, 'wb', 0)
    output_handle = open(OUTPUT_PIPE, 'rb')

    os.set_blocking(output_handle.fileno(), False)

    read_until(output_handle, ADD_SYMBOL_FILE_STR)
    print("Got add-symbol line!")

    # Grab the line, but ignore the file, we know it.
    #uefi_output = ' '.join(read_line(output_handle).split(' ')[2:])
    uefi_output = read_line(output_handle)

    gdb_line = f'add-symbol-file uefi_app.efi {uefi_output}'
    print(f'would use {gdb_line}')
    gdb.execute('interrupt')
    gdb.execute(gdb_line)

except Exception as e:
    print(f"Exception!! {e}")
    pass
finally:
    pass
    #qemu_process.kill()