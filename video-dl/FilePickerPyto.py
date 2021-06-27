import sys
from typing import List


def FilePickerPyto(
    file_types: List[str] = ["public.data"], allows_multiple_selection: bool = True
) -> List[str]:
    file_path_list: List[str]
    try:
        import sharing

        filePicker = sharing.FilePicker()
        filePicker.file_types = file_types
        filePicker.allows_multiple_selection = allows_multiple_selection
        sharing.pick_documents(filePicker)
        file_path_list = sharing.picked_files()
    except Exception:
        from FilePicker import GetFilePathByGUI

        file_path_list = list(GetFilePathByGUI())

    if len(file_path_list) == 0:
        input("ファイルが選択されませんでした。エンターを押すと終了します")
        sys.exit()
    return file_path_list


if __name__ == "__main__":
    print(FilePickerPyto())
