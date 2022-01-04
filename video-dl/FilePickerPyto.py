import sys
import sharing


def FilePickerPyto(
    file_types: list[str] = ["public.data"], allows_multiple_selection: bool = True
) -> list[str]:
    file_path_list: list[str]
    filePicker = sharing.FilePicker()
    filePicker.file_types = file_types
    filePicker.allows_multiple_selection = allows_multiple_selection
    sharing.pick_documents(filePicker)
    file_path_list = sharing.picked_files()
    if len(file_path_list) == 0:
        file_path_list = [input("ファイルパスを直接入力して下さい\n>>")]

    if len(file_path_list) == 1 and file_path_list[0] == "":
        input("ファイルが選択されませんでした。エンターを押すと終了します")
        sys.exit()
    return file_path_list


if __name__ == "__main__":
    print(FilePickerPyto())
