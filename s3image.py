import base64
import random
import string
import boto3
import requests
import logging
from botocore.exceptions import ClientError
from decouple import config

AWS_ACCESS_KEY_ID = config("ECS_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("ECS_AWS_SECRET_ACCESS_KEY")
AWS_BUCKET = config("ECS_AWS_STORAGE_BUCKET_NAME")
AWS_DEFAULT_REGION = config("ECS_AWS_S3_REGION_NAME")
AWS_USE_PATH_STYLE_ENDPOINT = False


def get_url(namefile):
    if namefile == None:
        return None
    if ".s3.amazonaws.com/" in namefile:
        namefile = namefile.split("amazonaws.com/")[1]
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        client_action = "get_object"

        method_parameters = {"Bucket": AWS_BUCKET, "Key": namefile}
        expires_in = 600
        url = s3_client.generate_presigned_url(
            ClientMethod=client_action, Params=method_parameters, ExpiresIn=expires_in
        )
        # print(url)
        return url
    if "production" in namefile or "local" in namefile:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        client_action = "get_object"

        method_parameters = {"Bucket": AWS_BUCKET, "Key": namefile}
        expires_in = 600
        url = s3_client.generate_presigned_url(
            ClientMethod=client_action, Params=method_parameters, ExpiresIn=expires_in
        )
        # print(url)
        return url
    return namefile


def aws_image(image_base64, data, pasta):
    # Decode the base64 image
    # Generate a random string with 14 letters
    random_letters = "".join(random.choices(string.ascii_letters, k=14))

    # Generate a random string with 4 numbers
    random_numbers = "".join(random.choices(string.digits, k=4))
    # print(data)
    data = str(data)
    mes = data[:7]
    dia = data[8:10]
    # Combine the two strings to get the final result
    file_name = (
        "local/"
        + pasta
        + "/"
        + str(mes)
        + "/"
        + str(dia)
        + "/"
        + str(dia)
        + "-"
        + random_letters
        + random_numbers
        + ".jpeg"
    )
    # Print the result
    if "," in image_base64:
        image_base64 = image_base64.split(",")[-1]
    image_data = base64.b64decode(image_base64)

    # Save the image to a ContentFile
    # image = ContentFile(image_data, name=file_name)

    # Connect to AWS S3
    # s3 = boto3.client(
    #     "s3",
    #     aws_access_key_id=AWS_ACCESS_KEY_ID,
    #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    # )
    # Save the image to S3
    # response = s3.put_object(Bucket=AWS_BUCKET, Key=file_name, Body=image)
    # s3.put_object(
    #     Bucket=AWS_BUCKET, Key=file_name, Body=image_data, ContentType="image/jpeg"
    # )
    return file_name


def s3document(document_base64, data, code, pasta):
    # Decode the base64 image
    # Generate a random string with 14 letters
    random_letters = "".join(random.choices(string.ascii_letters, k=14))

    # Generate a random string with 4 numbers
    random_numbers = "".join(random.choices(string.digits, k=4))
    # print(data)
    data = str(data)
    mes = data[:7]
    dia = data[8:10]
    if code == "":
        code = "662212"
    # Combine the two strings to get the final result
    file_name = (
        "production/"
        + code
        + "/documents"
        + pasta
        + str(mes)
        + "/"
        + str(dia)
        + "/"
        + str(dia)
        + "-"
        + random_letters
        + random_numbers
        + ".pdf"
    )
    if "," in document_base64:
        document_base64 = document_base64.split(",")[-1]
    document_data = base64.b64decode(document_base64)

    # Connect to AWS S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    # Save the image to S3
    # response = s3.put_object(Bucket=AWS_BUCKET, Key=file_name, Body=image)
    s3.put_object(
        Bucket=AWS_BUCKET,
        Key=file_name,
        Body=document_data,
        ContentType="application/pdf",
    )
    return file_name


def delete_url(namefile):
    if namefile == None:
        return None
    elif ".s3.amazonaws.com/" in namefile:
        namefile = namefile.split("amazonaws.com/")[1]
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        method_parameters = {"Bucket": AWS_BUCKET, "Key": namefile}
        s3_client.delete_object(**method_parameters)
        return "Deletado"
    else:
        return namefile


logger = logging.getLogger(__name__)


def generate_presigned_url(s3_client, client_method, method_parameters, expires_in):
    """
    Generate a presigned Amazon S3 URL that can be used to perform an action.

    :param s3_client: A Boto3 Amazon S3 client.
    :param client_method: The name of the client method that the URL performs.
    :param method_parameters: The parameters of the specified client method.
    :param expires_in: The number of seconds the presigned URL is valid for.
    :return: The presigned URL.
    """
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod=client_method, Params=method_parameters, ExpiresIn=expires_in
        )
        logger.info("Got presigned URL: %s", url)
    except ClientError:
        logger.exception(
            "Couldn't get a presigned URL for client method '%s'.", client_method
        )
        raise
    return url


def usage_demo():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    action = "get"

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    # s3_client = boto3.client("s3")
    client_action = "get_object" if action == "get" else "put_object"
    url = generate_presigned_url(
        s3_client,
        client_action,
        {"Bucket": AWS_BUCKET, "Key": AWS_SECRET_ACCESS_KEY},
        1000,
    )

    response = None
    if action == "get":
        response = requests.get(url)
    elif action == "put":
        try:
            with open(AWS_SECRET_ACCESS_KEY, "r") as object_file:
                object_text = object_file.read()
            response = requests.put(url, data=object_text)
        except FileNotFoundError:
            print(
                f"Couldn't find {AWS_SECRET_ACCESS_KEY}. For a PUT operation, the key must be the "
                f"name of a file that exists on your computer."
            )

    if response is not None:
        print("Got response:")
        print(f"Status: {response.status_code}")
        print(response.text)

    print("-" * 88)
