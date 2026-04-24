import os
import time
from datetime import date
from gDrive import GDrive
from base64 import b64decode
from uuid import uuid4

class Invoices:
    def __init__(self) -> None:
        #self._folder = '/mnt/hgfs/Pagos'
        #self._log = os.path.join(self._folder, 'invoices.log')
        self._drive = GDrive()
        self._principal_folder = 'Pagos'
        self._folder_id = self._drive.get_folder_id(self._principal_folder)
    
    def save_log(self, parent, child, file_name):
        pass
        # format_date = time.strftime('%d_%b_%Y-%H_%m', time.localtime())
        # with open(self._log, 'a') as log:
        #     log.write(f'{format_date},{parent},{child},{file_name}\n')
    
    def get_files(self, folder_name):
        return self._drive.get_files(folder_name)


    def save_file(self,parent:str, child,month,file_name, file_bytes):
        uploaded = {}
        format_date = time.strftime('%d_%b_%Y-%H_%m', time.localtime())
        y = str(date.today().year)
        file_extension = os.path.splitext(file_name)[1]
        file_name = f'{month.upper()}_{child+"_" if child else ""}{format_date}_{str(uuid4())}_{file_extension}'
        year_folder_id = self._drive.create_subfolder_if_not_exists(self._folder_id, y)
        child_id = self._drive.create_subfolder_if_not_exists(year_folder_id, parent)

        #child_id = self._drive.create_subfolder_if_not_exists(self._folder_id, f'{y}/{parent}')
        file_link = self._drive.upload_file(child_id, file_bytes, file_name)

        self.save_log(parent, child, file_name)
        
        uploaded['filename'] = f'{self._principal_folder}/{y}/{parent}/{child if child else ""}/{file_name}'
        uploaded['filelink'] = file_link
        return uploaded


    def upload(self, parent:str, child,month, file, b64=None):
        files = []
        if file:
            file_saved = self.save_file(parent, child, month, file.filename, file.read())
            files.append(file_saved)
        
        if b64:
            ext = b64.split(';')[0]
            file_bytes = b64decode(b64.replace(f'{ext};base64,',''))
            file_saved = self.save_file(parent, child, month, 'AA.png', file_bytes)
            files.append(file_saved)
        
        return files

