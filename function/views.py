import psutil, pytz, datetime, random, string, base64, boto3, smtplib
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from audits.serializer import AuditsRemovalSerializer
import backend.settings
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.db.utils import OperationalError
from django.http import JsonResponse

# fuso = timezone.get_current_timezone()
fuso = pytz.timezone("America/Sao_Paulo")

AWS_ACCESS_KEY_ID = config("ECS_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("ECS_AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = config("ECS_AWS_STORAGE_BUCKET_NAME")
AWS_BUCKET = config("ECS_AWS_S3_REGION_NAME")
# AWS_USE_PATH_STYLE_ENDPOINT = config("AWS_USE_PATH_STYLE_ENDPOINT")
# AWS_LOCAL = config("AWS_LOCAL")


def envia_email(email, assunto, conteudo):
    # Cria uma sessão com as suas credenciais da AWS
    message = MIMEMultipart()
    message["From"] = backend.settings.ECS_MAIL_FROM_ADDRESS
    message["To"] = email
    message["Subject"] = assunto
    message.attach(MIMEText(conteudo, "plain"))
    try:
        with smtplib.SMTP(
            backend.settings.ECS_MAIL_HOST, backend.settings.ECS_MAIL_PORT
        ) as server:
            server.starttls()
            server.login(
                backend.settings.ECS_MAIL_USERNAME,
                backend.settings.ECS_MAIL_PASSWORD,
            )
            server.sendmail(
                backend.settings.ECS_MAIL_FROM_ADDRESS, email, message.as_string()
            )
    except Exception as e:
        print(e)
        return False
    return True


def date_format(date):
    if date:
        if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            return date.strftime("%d/%m/%Y")
        elif isinstance(date, str):
            try:
                datetime_obj = timezone.datetime.strptime(
                    date[:19], "%Y-%m-%dT%H:%M:%S"
                )
                localized_datetime = timezone.make_aware(
                    datetime_obj, timezone.utc
                ).astimezone(fuso)
                return localized_datetime.strftime("%d/%m/%Y %H:%M")
            except ValueError:
                try:
                    datetime_obj = timezone.datetime.strptime(date, "%Y-%m-%d")
                    return datetime_obj.strftime("%d/%m/%Y")
                except ValueError:
                    return date
        else:
            localized_datetime = timezone.make_aware(date, timezone.utc).astimezone(
                fuso
            )
            return localized_datetime.strftime("%d/%m/%Y %H:%M")
    return None


def serializer_function(data, serializer_type):
    data["created_at"] = timezone.now()
    data["updated_at"] = timezone.now()
    try:
        serializer = serializer_type(data=data)
    except Exception as e:
        return False, str(e), None, status.HTTP_400_BAD_REQUEST

    try:
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        obj = serializer_type(obj)
        return True, "Objeto criado", obj.data, status.HTTP_201_CREATED
    except ValidationError as e:
        error_dict = {}
        for field, errors in e.detail.items():
            error_dict[field] = [str(error) for error in errors]
        return False, error_dict, None, status.HTTP_400_BAD_REQUEST


def generate_random_string(length):
    characters = string.ascii_lowercase + string.digits
    random_string = "".join(random.choices(characters, k=length))
    return random_string


def create_filename_document_date(document_base64, pasta, extension, contenttype):
    random_letters = "".join(random.choices(string.ascii_letters, k=14))
    random_numbers = "".join(random.choices(string.digits, k=4))
    date = str(timezone.now())
    mes = date[:7]
    dia = date[8:10]
    # Combine the two strings to get the final result
    file_name = (
        "production/"
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
        + extension
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
    s3.put_object(
        Bucket=AWS_BUCKET,
        Key=file_name,
        Body=document_data,
        ContentType=contenttype,
    )
    return file_name


def delete_objects(remove_list):
    for obj in remove_list:
        obj.delete()


start_time = timezone.now()


class ViewSuccess:
    # Função para recuperação de senha
    @csrf_exempt
    def ok(request):
        uptime = timezone.now() - start_time
        days = uptime.days
        months = days // 30
        remaining_days = days % 30
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_string = f"{months} meses, {remaining_days} dias, {hours} horas, {minutes} minutos, {seconds} segundos"

        # Teste de conexão com o banco de dados
        connection_db = False
        try:
            # Test a simple SELECT query
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result is not None:
                    connection_db = "Conexão com o banco de dados bem-sucedida."
                else:
                    connection_db = (
                        "Erro: Não foi possível ler dados do banco de dados."
                    )
        except OperationalError as e:
            connection_db = "Erro de conexão com o banco de dados:" + str(e)

        # Memória utilizada
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_usage_gb = memory_info.rss / 1073741824
        memory_message = f"{memory_usage_gb:.3f} GB"

        return JsonResponse(
            {
                "success": True,
                "message": "API Disponível",
                "Tempo do servidor em execução": uptime_string,
                "Conexão": connection_db,
                "Memória": memory_message,
            },
            status=status.HTTP_200_OK,
        )
