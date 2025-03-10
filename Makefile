all: clean uefi_app.debug.efi uefi_app.efi

uefi_app.debug.efi: uefiapp.so
	objcopy -j .text -j .sdata -j .data -j .rodata -j .dynamic -j .dynsym  -j .rel -j .rela -j .rel.* -j .rela.* -j .reloc -j .debug_info -j .debug_abbrev -j .debug_loc -j .debug_aranges -j .debug_line -j .debug_macinfo -j .debug_str -j .debug_line_str --target efi-app-x86_64 --subsystem=10 uefi_app.so uefi_app.debug.efi

uefi_app.efi: uefiapp.so
	objcopy -j .text -j .sdata -j .data -j .rodata -j .dynamic -j .dynsym  -j .rel -j .rela -j .rel.* -j .rela.* -j .reloc --target efi-app-x86_64 --subsystem=10 uefi_app.so uefi_app.efi

uefiapp.so: main.o
	#ld -shared -Bsymbolic -L./gnu-efi/x86_64/lib -L./gnu-efi/x86_64/gnuefi -T./gnu-efi/gnuefi/elf_x86_64_efi.lds ./gnu-efi/x86_64/gnuefi/crt0-efi-x86_64.o main.o -o uefi_app.so -lgnuefi -lefi
	ld -shared -Bsymbolic -L/usr/lib -T/usr/lib/elf_x86_64_efi.lds /usr/lib/crt0-efi-x86_64.o main.o -o uefi_app.so -lgnuefi -lefi

main.o: main.c
	gcc -g -I/usr/include/efi -fpic -ffreestanding -fno-stack-protector -fno-stack-check -fshort-wchar -mno-red-zone -maccumulate-outgoing-args -c main.c -o main.o

clean:
	rm -f main.o uefi_app.so uefi_app.efi uefi_app.debug.efi

