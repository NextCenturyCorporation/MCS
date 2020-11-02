import io
import pathlib

import boto3
import PIL


class S3Uploader():
    '''Upload evaluation files to an AWS S3 bucket.

    Leverages the AWS credentials written from the controller's configuration.
    '''

    def __init__(self, s3_bucket: str):
        self.client = boto3.client('s3')
        self.bucket = s3_bucket

    def upload_video(self,
                     video_path: pathlib.Path,
                     s3_filename: str) -> None:
        '''Uploads mp4 video files from disk to AWS S3

        Args:
            video_path (pathlib.Path): path to video file
            s3_filename (str): name to give video in s3

        Returns:
            None
        '''
        print(f"Uploading {video_path} to {self.bucket} as {s3_filename}")
        # self._upload_file(
        #     filepath=video_path,
        #     bucket=self.bucket,
        #     s3_filename=s3_filename,
        #     mimetype='video/mp4'
        # )

    def upload_image(self,
                     image: PIL.Image.Image,
                     s3_filename: str) -> None:
        '''Uploads in-memory PIL images to AWS S3

        Args:
            image (PIL.Image.Image): image bytes to upload
            s3_filename (str): name to give image in s3

        Returns:
            None
        '''
        in_memory_file = io.BytesIO()
        image.save(fp=in_memory_file, format='png')
        in_memory_file.seek(0)

        self._upload_object(
            in_memory_file=in_memory_file,
            bucket=self.bucket,
            s3_filename=s3_filename,
            mimetype='image/png'
        )

    def upload_history(self,
                       history_path: pathlib.Path,
                       s3_filename: str) -> None:
        '''Uploads scene history from disk to AWS S3

        Args:
            history_path (pathlib.Path): path to history json file
            s3_filename (str): name to give file in s3

        Returns:
            None
        '''
        print(f"Uploading {history_path} to {self.bucket} as {s3_filename}")
        # self._upload_file(
        #     filepath=history_path,
        #     bucket=self.bucket,
        #     s3_filename=s3_filename,
        #     mimetype='application/json'
        # )

    def _upload_file(self,
                     filepath: pathlib.Path,
                     bucket: str,
                     s3_filename: str,
                     mimetype: str) -> None:
        '''Upload a file from disk to AWS S3 bucket

        Args:
            filepath (pathlib.Path): the file path on disk
            bucket (str): the S3 bucket to upload the file to
            s3_filename (str): rename s3 file
            mimetype (str): mimetype for the file to upload

        Returns:
            None
        '''
        self.client.upload_file(
            str(filepath),
            bucket,
            s3_filename,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': mimetype,
            }
        )

    def _upload_object(self,
                       in_memory_file: io.BytesIO,
                       bucket: str,
                       s3_filename: str,
                       mimetype: str) -> None:
        '''Upload an in-memory file object to AWS S3 bucket

        Args:
            in_memory_file (io.BytesIO): the in-memory file to upload
            bucket (str): the s3 bucket to upload to
            s3_filename (str): s3 filename
            mimetype (str): mimetype of the in-memory file

        Returns:
            None
        '''
        self.client.upload_fileobj(
            in_memory_file,
            bucket,
            s3_filename,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': mimetype,
            }
        )
