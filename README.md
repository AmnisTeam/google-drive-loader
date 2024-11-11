![Static Badge](https://img.shields.io/badge/python-%232968E5?style=for-the-badge&logo=Python&logoColor=white)
![Static Badge](https://img.shields.io/badge/PyDrive-%23DB522F?style=for-the-badge&logo=googledrive&logoColor=white)
![Static Badge](https://img.shields.io/badge/pathspec-%23F5940F?style=for-the-badge&logo=opensourcehardware&logoColor=white)

GoogleDriveLoader is a small repository that contains python code that allows you to conveniently upload files and folders from your computer to any location in Google drive.

## Discription
It contains the DriveLoader class, which contains all the main functionality, as well as an additional demo.py file with a demo of the code. 
The DriveLoader class can upload a specified file from the computer to a specified directory on the disk (you need to specify the path along with the file name) using the upload_file() method, 
and can also upload folders using the upload_folder() method. Also, a mechanism similar to .gitignore, which allows you to ignore paths that do not need to be uploaded to the disk.

## How to run?
For the code to work, you need to log in to Google Cloud Console and get the secret keys from there, which PyDrive works with - just put them in the same folder where the executable file is located (in our case, demo.py), 
after which everything will work. This is done quite simply if you strictly follow the tutorials:
|  Language  |                     Link                    |
| ---------- | ------------------------------------------- |
| In English | https://www.youtube.com/watch?v=tamT_iGoZDQ |
| In Russian | https://www.youtube.com/watch?v=QxVl8m54vnk |
