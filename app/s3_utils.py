import boto3
from .config import settings

def upload_image_to_s3(image_bytes: bytes, image_id: str, content_type: str = "image/jpeg") -> str:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION,
    )
    key = f"images/{image_id}.jpg"
    s3.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
        Body=image_bytes,
        ContentType=content_type
    )
    url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{key}"
    return url

# only for the first time to create the bucket
def create_bucket_if_not_exists(bucket_name: str = "imagemtadata2025"):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION,
    )
    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if bucket_name not in buckets:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": settings.AWS_S3_REGION}
        )
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.") 