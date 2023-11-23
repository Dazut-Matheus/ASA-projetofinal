# (1) sistema operacional Ubuntu-18.04
FROM ubuntu:22.04


# Ajustar para python3.9
RUN apt update -y; apt upgrade -y
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-cache policy python3.9

# Instalando o cron
RUN apt-get install -y cron

# Variaveis de ambientes para tzdata
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

# (2) Instalar as depedencias
RUN apt update -y; apt install -y \
    git \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    libx11-dev \
    libgtk-3-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    software-properties-common \
    python3 \
    python3-dev \
    python3-pip \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    libmysqlclient-dev \
    mysql-client

# (3)  Crio o diretorio backend e declaro como area de trabalho
RUN mkdir /backend
WORKDIR /backend

# (4) Instalação dos Compiladores
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:ubuntu-toolchain-r/test
RUN apt update -y; apt install -y gcc g++

# (5) Copio o meu req.txt, adiciono scikit build e req
COPY req.txt /backend/

# RUN python3 -m pip install --upgrade pip
RUN python3.9 -m pip install scikit-build
RUN python3.9 -m pip install -r req.txt
RUN python3.9 -m pip install mysql-connector-python

ADD . .

# Gera o .env
RUN cd /backend
#RUN cp docker.env ./.env
#COPY .env ./

## (6) Ao final de tudo, executo o python3 manage.py runserver
EXPOSE 80
#CMD ["python3.9", "manage.py", "runserver", "0.0.0.0:8000"]
CMD python3.9 manage.py runserver 0.0.0.0:80