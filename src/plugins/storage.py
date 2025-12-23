import os

import boto3


class S3FSStorage:
    """Storage to save files from test in S3 bucket."""

    def __init__(
        self,
        bucket_name: str = os.environ.get("AWS_STORAGE_BUCKET_NAME", ""),
        aws_access_key_id: str = os.environ.get("AWS_ACCESS_KEY_ID", ""),
        aws_secret_access_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        aws_session_token: str = os.environ.get("AWS_SESSION_TOKEN", ""),
        region_name: str = os.environ.get("AWS_REGION", ""),
    ):
        super().__init__()
        self.bucket = bucket_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
        )

    def save_file_obj(self, content: bytes, filename: str, **kwargs) -> str:
        """Upload file to S3 and get it's url."""
        self.s3_client.put_object(
            Body=content,
            Bucket=self.bucket,
            Key=filename,
            **kwargs,
        )
        return f"{self.s3_client.meta.endpoint_url}/{self.bucket}/{filename}"
