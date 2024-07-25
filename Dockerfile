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

RUN curl -fsSL https://ollama.com/install.sh | sh


RUN pip3 install --no-cache-dir ollama python-dotenv thread openai-whisper slack_bolt

COPY . /workspace
WORKDIR /workspace

RUN chmod +x /workspace/run-ollama.sh \
    && ./run-ollama.sh
RUN chmod +x /workspace/entrypoint.sh

EXPOSE 8501
ENTRYPOINT ["./entrypoint.sh"]

