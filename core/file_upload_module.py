import uuid

from datetime import datetime

class FileHandler:
    def __init__(self, client):
        self.client = client
    
    def upload(self, file):
        return self.client.upload(file)
    
    def delete(self, file_url):
        return self.client.delete(file_url)
    
class AwsUploader:
    def __init__(self, client, config):
        self.client = client
        self.config = config
    
    def create_file_name(self, file):
        file_id    = str(uuid.uuid4())
        image_url  = f'http://{self.config.get("bucket_name")}.s3.ap-northeast-2.amazonaws.com/'+file_id

        return image_url.replace(" ", "/")
    
    def upload(self, file):
        if not file:
            return None

        try: 
            extra_args  = {'ContentType' : file.content_type}
            file_id     = str(uuid.uuid4())
            bucket_name = self.config.get("bucket_name")
            
            self.client.upload_fileobj(
                file,
                bucket_name,
                file_id,
                ExtraArgs = extra_args
            )

            return f'http://{self.config.get("bucket_name")}.s3.ap-northeast-2.amazonaws.com/'+file_id

        except:
            return None

    def delete(self, file_name):
        bucket_name = self.config.get("bucket_name")
        
        return self.client.delete_object(bucket=bucket_name, Key=f'{file_name}')