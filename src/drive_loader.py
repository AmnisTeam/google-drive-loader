import os
import posixpath
from pydrive.drive import GoogleDrive

class DriveLoader():
    def __init__(self, drive: GoogleDrive):
        self.drive = drive
    
    def create_folder(self, drive_folder_path: str, parent = None):
        drive_folder_path = posixpath.normpath(drive_folder_path)

        parent = parent
        dir = drive_folder_path
        dir_names = []
        if parent is None:
            while len(dir) > 0:
                folders_list = self.drive.ListFile({'q': f"title = '{dir}' and mimeType = 'application/vnd.google-apps.folder'"}).GetList()
                if len(folders_list) > 0:
                    parent = folders_list[0]['id']
                    break
                
                dir_parts = posixpath.split(dir)
                dir = dir_parts[0]
                dir_names.append(dir_parts[1])
        else:
            dir_names = [posixpath.basename(drive_folder_path)]
        
        for name in dir_names[::-1]:
            folder_metadata = {
                'title': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [{'id': parent}] if parent is not None else []
            }
            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            parent = folder['id']
        
        return parent


    def upload_file(self, file_path: str, drive_file_path: str, parent=None):
        file_path = posixpath.normpath(file_path)
        drive_file_path = posixpath.normpath(drive_file_path)

        filename = posixpath.basename(drive_file_path)

        drive_folder_path = posixpath.dirname(drive_file_path)
        folder_id = self.create_folder(self.drive, drive_folder_path, parent) if parent is None else parent # Если вдруг такой папки нет

        file_metadata = {
            'title': filename,
            'parents': [{'id': folder_id}]
        }
        gfile = self.drive.CreateFile(file_metadata)
        gfile.SetContentFile(file_path)
        gfile.Upload()
    

    def upload_folder(self, folder_path: str, drive_folder_path: str, parent=None):
        folder_path = posixpath.normpath(folder_path)
        drive_folder_path = posixpath.normpath(drive_folder_path)

        parent = self.create_folder(self.drive,  drive_folder_path, parent)

        for name in os.listdir(folder_path):
            path = posixpath.join(folder_path, name)
            sub_drive_path = posixpath.join(drive_folder_path, name)
            if posixpath.isfile(path):
                self.upload_file(self.drive, path, sub_drive_path, parent)
            else:
                self.upload_folder(self.drive, path, sub_drive_path, parent)
