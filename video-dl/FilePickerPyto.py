import sharing

from typing import List


def FilePickerPyto(
    file_types: List[str] = ["public.data"], multiple_selection: bool = True
) -> List[str]:
    filePicker = sharing.FilePicker()
    filePicker.file_types = file_types
    filePicker.allows_multiple_selection = multiple_selection

    sharing.pick_documents(filePicker)
    file_path_list = sharing.picked_files()
    return file_path_list


if __name__ == "__main__":
    print(FilePickerPyto())
