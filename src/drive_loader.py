import os
import posixpath
from pydrive.drive import GoogleDrive
import pathspec
import json

class DriveLoader():
    def __init__(self, drive: GoogleDrive, driveignore_path: str = ".driveignore", drivecache_path: str = ".drivechache", save_cache=True, sync_mode=False):
        self.drive = drive
        self.sync_mode = sync_mode

        with open(driveignore_path, "r", encoding="utf-8") as file:
            ignore_rules = file.readlines()
        
        self.spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_rules)

        self.save_cache = save_cache
        self.drivecache_path = drivecache_path
        self.cache = {}
        if os.path.exists(drivecache_path):
            with open(drivecache_path, "r", encoding="utf-8") as file:
                self.cache = json.load(file)

        self.__del_cache = {}
    

    def check_path(self, drive_path: str, parent_id="root"):
        drive_path = posixpath.normpath(drive_path)
        parts = drive_path.split("/")

        objects = []
        for name in parts:
            folder_list = self.drive.ListFile({'q': f"'{parent_id}' in parents and title = '{name}' and trashed = false"}).GetList()
            
            if len(folder_list) == 0:
                break

            parent_id = folder_list[0]["id"]
            objects.append(folder_list[0])
        return objects


    def create_folder(self, drive_folder_path: str, parent = None):
        drive_folder_path = posixpath.normpath(drive_folder_path)

        parent = parent
        dir = drive_folder_path
        dir_names = []
        if parent is None:
            folders = self.check_path(drive_folder_path)
            parent = folders[-1]["id"] if len(folders) > 0 else None
            dir_names = drive_folder_path.split("/")[len(folders):]
        else:
            dir_names = [posixpath.basename(drive_folder_path)]
        
        for name in dir_names:
            folder_metadata = {
                'title': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [{'id': parent}] if parent is not None else []
            }
            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            parent = folder['id']
        
        return parent


    def delete_file(self, drive_file_path: str):
        drive_file_path = posixpath.normpath(drive_file_path)

        objects = self.check_path(drive_file_path)
        assert len(objects) == len(drive_file_path.split("/")), "File path is incorrect."
        objects[-1].Delete()


    def delete_file_by_id(self, file_id: str, use_try: bool = False):
        if use_try:
            try:
                file = self.drive.CreateFile({'id': file_id})
                file.Delete()
            except:
                pass
        else:
            file = self.drive.CreateFile({'id': file_id})
            file.Delete()


    def replace_file(self,  file_path: str, drive_file_id: str):
        file_path = posixpath.normpath(file_path)

        file_metadata = {
            "id": drive_file_id
        }

        gfile = self.drive.CreateFile(file_metadata)
        gfile.SetContentFile(file_path)
        gfile.Upload()
        return gfile


    def upload_file(self, file_path: str, drive_file_path: str, parent=None, root=True):
        file_path = posixpath.normpath(file_path)
        drive_file_path = posixpath.normpath(drive_file_path)
        
        is_need_save = False
        if not self.spec.match_file(file_path):
            if file_path in self.__del_cache:
                del self.__del_cache[file_path]

            file_in_cache = file_path in self.cache
            if not file_in_cache:
                objects = self.check_path(drive_file_path if parent == None else posixpath.basename(drive_file_path), "root" if parent == None else parent) # ПРОВЕРИТЬ!!!!!
            replace_no_cache_object = ( (len(objects) == len(drive_file_path.split("/"))) if parent == None else (len(objects) == 1) )
            mtime = os.path.getmtime(file_path)
            if replace_no_cache_object:
                is_need_save = True
                file = self.replace_file(file_path, objects[-1]["id"])
                self.cache[file_path] = [mtime, file["id"]]
            elif mtime > self.cache[file_path][0]:
                is_need_save = True
                file = self.replace_file(file_path, self.cache[file_path][1])
                self.cache[file_path] = [mtime, file["id"]]
            else:
                is_need_save = True
                filename = posixpath.basename(drive_file_path)
                drive_folder_path = posixpath.dirname(drive_file_path)
                folder_id = self.create_folder(drive_folder_path, parent) if parent is None else parent # Если вдруг такой папки нет

                file_metadata = {
                    'title': filename,
                    'parents': [{'id': folder_id}]
                }
                gfile = self.drive.CreateFile(file_metadata)
                gfile.SetContentFile(file_path)
                gfile.Upload()

                self.cache[file_path] = [mtime, gfile["id"]]
            
            if self.save_cache and root and is_need_save:
                    with open(self.drivecache_path, "w") as file:
                        json.dump(self.cache, file)
        
        return is_need_save

    

    def upload_folder(self, folder_path: str, drive_folder_path: str, parent=None, root=True):
        folder_path = posixpath.normpath(folder_path) + '/'
        drive_folder_path = posixpath.normpath(drive_folder_path) + '/'

        if root:
            self.__del_cache = self.cache.copy()

        is_need_save = False
        if not self.spec.match_file(folder_path):
            if folder_path not in self.cache:
                parent = self.create_folder(drive_folder_path, parent)
            else:
                parent = self.cache[folder_path][1]

            if folder_path in self.__del_cache:
                del self.__del_cache[folder_path]

            mtime = os.path.getmtime(folder_path)
            self.cache[folder_path] = [mtime, parent]

            for name in os.listdir(folder_path):
                path = posixpath.join(folder_path, name)
                sub_drive_path = posixpath.join(drive_folder_path, name)
                if posixpath.isfile(path):
                    res = self.upload_file(path, sub_drive_path, parent, root=False)
                    is_need_save = True if is_need_save else res
                else:
                    res = self.upload_folder(path, sub_drive_path, parent, root=False)
                    is_need_save = True if is_need_save else res

        if root:
            if self.sync_mode:
                for path, (time, id) in self.__del_cache.items():
                    self.delete_file_by_id(id, use_try=True)
                    del self.cache[path]
                    is_need_save = True
            self.__del_cache.clear()

        if self.save_cache and root and is_need_save:
            with open(self.drivecache_path, "w") as file:
                json.dump(self.cache, file, indent=4)

        return is_need_save
