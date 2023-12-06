FROM ubuntu:20.04

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="${PYTHONPATH}:/app" \
    PIP_DEFAULT_TIMEOUT=100

RUN exec bash

# RUN chmod 744 /home/app_user

RUN apt-get update && apt-get install -y --no-install-recommends software-properties-common \
    libsm6 libxext6 libxrender-dev curl \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:deadsnakes/ppa &&  \
    apt-get install -y build-essential python3.9 python3.9-dev python3-pip && \
    curl -O https://bootstrap.pypa.io/get-pip.py && \
    python3.9 get-pip.py && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN apt-get update -qqy \
    && apt-get autoclean \
    && apt-get autoremove \
    && apt-get install -y wget \
    && apt-get install -y build-essential \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

ENV CONDA_DIR=/opt/conda

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda

ENV PATH=$CONDA_DIR/bin:$PATH

RUN conda create -n audio-processing python=3.9

RUN conda init bash

SHELL ["conda", "run", "-n", "audio-processing", "/bin/bash", "-c"]

RUN pip install --upgrade pip

RUN pip install Cython==3.0.5

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#RUN groupadd -g 1000 app_group
#
#RUN useradd -g app_group --uid 1000 app_user
#
#RUN chown -R app_user:app_group /app
#
#USER app_user

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
