import os.path
import io
import json
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from database.tables import Parameters
from database.dbmanager import DbManager

class GDrive:
    def __init__(self) -> None:
      self._SCOPES = ["https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive.metadata"]
      self._service = None
      self._parameter_name = 'gdrive_token'
      self._db = DbManager()
      self.login()
    
    def login(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token = self._db.get_parameter(self._parameter_name)
        
        if token:
            #creds = Credentials.from_authorized_user_file("token.json", self._SCOPES)
            creds = Credentials.from_authorized_user_info(json.loads(token), self._SCOPES)
            
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self._SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                self._db.create_parameter(self._parameter_name, creds.to_json())
                # with open("token.json", "w") as token:
                #     token.write(creds.to_json())
        try:
           self._service = build("drive", "v3", credentials=creds)
        except Exception as e:
           print(e)

    def create_subfolder_if_not_exists(self, parent_folder_id, subfolder_name):
        # Query to check if subfolder exists
        query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{subfolder_name}'"
        results = self._service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        if items:
            return items[0]['id']
        else:
            # Subfolder does not exist, create it
            file_metadata = {
                'name': subfolder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            folder = self._service.files().create(body=file_metadata, fields='id').execute()
            print(f"Subfolder '{subfolder_name}' created.")
            return folder.get('id')

    def get_subfolder_id(self, parent_id, folder_name):
        query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
        results = self._service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        if not items:
            print(f'Folder "{folder_name}" not found.')
            return None
        return items[0]['id']
    
    def get_folder_id(self, folder_name:str):
    
        """Retrieve the folder ID for a folder with a specific name."""
        try:
            results = self._service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            items = results.get('files', [])
            
            if not items:
                return None
            
            # If multiple folders have the same name, just return the first one
            folder_id = items[0]['id']
            print(f"Found folder '{folder_name}' with ID: {folder_id}")
            return folder_id
    
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def get_files(self, folder_name:str):
        files = []
        folder_id = self.get_folder_id('Pagos')
        sub_folder_id = self.get_subfolder_id(folder_id, folder_name)
        query = f"'{sub_folder_id}' in parents"
        results = self._service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        if items:
            for item in items:
                files.append(item["name"])
        
        return files
    
    def get_file_link(self, file_id):
        file_metadata = self._service.files().get(fileId=file_id, fields='webViewLink').execute()
        file_link = file_metadata.get('webViewLink')
        return file_link
    
    def upload_file(self, folder_id, file_bytes, file_name):
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        # Crear un stream de bytes
        file_stream = io.BytesIO(file_bytes)
        media = MediaIoBaseUpload(file_stream, mimetype='application/octet-stream', resumable=True)
        file = self._service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File '{file_name}' uploaded.")
        return self.get_file_link(file["id"])



if __name__ == '__main__':
    g = GDrive()
    g.get_file_link('15tpW_ixpTC3vkMxXsdaSI8BcvlO_uf4h')
    # pagos_id = g.get_folder_id('Pagos')
    # g.create_subfolder_if_not_exists(pagos_id, 'Recordar')