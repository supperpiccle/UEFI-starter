dd if=/dev/zero of=disk.img bs=1M count=64

# Put a FAT filesystem on it (use -F for FAT32, otherwise it's automatic)
mformat -i disk.img ::

# Copy the app to the disk.
mcopy -i disk.img ./uefi_app.efi ::
mcopy -i disk.img ./startup.nsh ::

# List files
mdir -i disk.img ::

# Run the system.
$PREFIX/bin/qemu-system-x86_64 -pflash OVMF.fd -drive unit=1,file=disk.img -net none -s -enable-kvm -monitor telnet:127.0.0.1:55555,server,nowait #assumed gdb debug port 1234 