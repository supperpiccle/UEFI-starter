#include <efi.h>
#include <efilib.h>

static void
__attribute__((__optimize__("0")))
debug_hook(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE* SystemTable)
{
	EFI_LOADED_IMAGE *loaded_image = NULL;
    EFI_STATUS status;

	status = uefi_call_wrapper(SystemTable->BootServices->HandleProtocol,
                               3,
                               ImageHandle,
                               &LoadedImageProtocol,
                               (void **)&loaded_image);
    if (EFI_ERROR(status)) {
        Print(L"handleprotocol: %r\n", status);
    }

    Print(L"Image base:\n0x%lx\n", loaded_image->ImageBase);
	Print(L"Pausing for debugger attachment.\n");

	int wait = 1;
    while (wait) {
		__asm__ __volatile__("pause");
    }
}

EFI_STATUS
EFIAPI
efi_main (EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable)
{
  InitializeLib(ImageHandle, SystemTable);
  Print(L"Hello, world!\n");
  debug_hook(ImageHandle, SystemTable);
  return EFI_SUCCESS;
}