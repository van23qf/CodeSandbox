FROM python:3.12-slim

RUN useradd --create-home --shell /bin/bash sandbox

WORKDIR /home/sandbox/code

RUN chown sandbox:sandbox /home/sandbox/code

USER sandbox

CMD ["python", "/home/sandbox/code/main.py"]
