FROM python:3.11


LABEL maintainer=onlyxool@gmail.com

ARG LC_ALL="C"
ARG DEBIAN_FRONTEND="noninteractive"
ARG TZ="Etc/UTC"
RUN ln -snf /usr/share/zoneinfo/"${TZ}" /etc/localtime && echo "${TZ}" >/etc/timezone

RUN apt-get update && apt-get install -y --no-install-recommends \
	vim \
	curl \
	ffmpeg \
	python3-dev \
	python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir ollama python-dotenv flask thread openai-whisper slack_bolt numpy==1.26.4

COPY . /workspace
WORKDIR /workspace

EXPOSE 80

CMD ["/bin/bash", "entrypoint.sh"]
