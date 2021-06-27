from sharing


def FilePickerPyto() -> str:
    filePicker = sharing.FilePicker()
    filePicker.file_types = ["public.data"]
    filePicker.allows_multiple_selection = False
    filePicker.completion = file_picked
    sharing.pick_documents(filePicker)


def file_picked() -> None:
    files = sharing.picked_files()
    sharing.share_items(files)

