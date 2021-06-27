import sharing



def FilePickerPyto():
    filePicker = sharing.FilePicker()
    filePicker.file_types = ["public.data"]
    filePicker.allows_multiple_selection = False
    
    sharing.pick_documents(filePicker)
    file_path_list = sharing.picked_files()
    return file_path_list

 
if __name__ == "__main__":
    print(FilePickerPyto()) 


