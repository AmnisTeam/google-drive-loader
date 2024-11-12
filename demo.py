from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from src.drive_loader import DriveLoader

if __name__ == "__main__":
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    drive_loader = DriveLoader(drive, sync_mode=True)
    drive_loader.upload_folder("test", "SomeFolder/ererer/test_folder1/test")