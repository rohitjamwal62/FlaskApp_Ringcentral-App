import boto3

def check_file_exists(bucket_name, prefix, file_name):
    # Initialize a session using your AWS access and secret keys
    session = boto3.Session(aws_access_key_id='AKIA2IU7S34G2C6SKYHQ',
                aws_secret_access_key='Qjv2Z+vOvGYPrGLLlAyraGU1Rro+Boj9LaGL9J7g')
    # Create an S3 client
    s3 = session.client('s3')
    # List objects in the bucket with the specified prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    # Check if the specified file_name exists in the listed objects
    for content in response.get('Contents', []):
        if content['Key'] == f"{prefix}{file_name}":
            return True
    return False

