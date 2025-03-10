# Starter UEFI Project

## Motivation
There is literature online that describes how to setup a uefi project, but this template is much much nicer to work with.  This project contains a starter uefi app as well as a script to automatically load symbols for your UEFI app.

## How To Use
Personally, this was written in a WSL environment.  You can write UEFI apps in Windows, but using Linux is just easier for UEFI development in my experience.

### One Time Setup
sudo setup.sh
pip install -r requirements.txt

### Building the App
```
make
```
https://wiki.osdev.org/UEFI_App_Bare_Bones is what the makefile is inspired from.

One thing worth mentioning here is that we build the app as an elf file, but then copy sections around to create a pe file.  This is because UEFI applications are pe files with just a few supported sections.  If you attempt to launch a pe file which has debug sections in UEFI, it'll simply not work.  Will refuse to load.  For the purpose of debugging we will keep the elf file with debug sections for our local debugger, and the stripped, pe file version on the uefi system to run.  Even though the executable formating is different, everything still seems to work which makes sense: the debugging symbols simply take an address in the .text or .data section and give you a source line number. 


### Launch QEMU
sudo launch_qemu.sh

This script will create a 64 megabyte fat32 disk, copy uefi_app.efi and startup.nsh files to it, and then launch qemu.  The reason we run sudo here is because we use kvm. Trust me you want kvm.  True emulation is way too slow in my experience.

When QEMU launches, it'll wait 5ish seconds (this is what the OVMF firmware does), and then run the app.

As for what some of the files here are:
* uefi_app.efi is the dummy uefi app that is compiled.
* startup.nsh is a special file you can drop on the drive to automatically run some commands.  In our case, we just want to run our dummy app.
* OVMF.fd is a UEFI complient firmware I compiled form the edk2 project.  It is what implements the UEFI specification.

#### The Dummy App
The dummy app is super small.  It calls the necessary InitializeLib function needed if using gnu-efi and then calls "debug_hook"  debug_hook gets the LoadedImageProtocol to print where the image is loaded.  This is simply to compare with what we compute in the gdb script which is described later.  Lastly, the dummy app sits in an active wait.  Once you connect via a debugger, you can set wait to 0 and get out of the loop.

### To Debug
Once you have launched the app and it is currently awaiting debug attachment, you have two ways to debug:
* Use the Attach To QEMU with GDB debug option in vscode.
* Manually attach with gdb.

To manually attach with gdb:
```
target remote localhost:1234
source load_symbols.py
load-symbol $rip uefi_app.so
```

#### Symbol Loading
Loading symbols for a UEFI app is a bit different than on a normal system.  Normally, the OS provides a nice an elegant interface to debug another user mode app.  Thread suspension, ability to get base address via some api call, and not having to go through QEMU being some nice to haves that we don't have in a UEFI environment.

Thread suspension is sorta handled by having the busy wait in the dummy app; it's about the best we got.

The base address question is much more annoying to deal with.  Whenever you launch a UEFI app, the firmware is free to relocate the binary wherever it wants. This is problematic for us because the debugger needs to know where the app is located to be able to use symbols.  In this environment, there isn't a standard api call that the debugger can call to determine the base address(perhaps some future work is to have gdb launch another uefi app to get the base address of this process as a stand in for what the OS normally provides.). Most tutorials you read will tell you to have the app print it's base address and then you copy that base address to tell gdb where it is like
```
add-symbol-file debug.myOS.efi 0x2EE33000 -s .data 0x2EE3c000
```
That simply won't work for me!  I suck at programming and need quicker iteration and this will drive me insane!

To make this somewhat more automatic, I heavily relied on https://github.com/x1tan/rust-uefi-runtime-driver/blob/master/load-symbols.py.  (ok I just changed a couple pieces to work better with my template) which creates a new gdb command "load-symbols".

The idea behind "load-symbols" is that it will take a provided address and walk memory backwards until it hits the magic "MZ" bytes in a pe file which also indicates the beginning of the pe file.  Once it finds the "MZ" bytes, then it has found the base address!  With the base address found, and the symbol file provided, it can automatically load the symbols.  This assumes that the base address is kinda near the beginning of the pe file.  If there happens to be another "MZ" between the breakpoint and the beginning of the file, this won't work.

In the building section, I talked about how we had the elf version with debugging symbols and a stripped pe version of the application.  So far, this mismatch doesn't seem to screw anything up, and it all seems to work for me.