FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3.11 python3-pip ffmpeg git \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN pip install --upgrade pip && pip install \
    demucs==4.0.1 \
    torch==2.3.0 \
    torchaudio==2.3.0 \
    boto3==1.34.0

COPY handler.py .

CMD ["python", "handler.py"]