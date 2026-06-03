FROM node:22-slim

RUN useradd --create-home --shell /bin/bash sandbox

WORKDIR /home/sandbox/code

RUN chown sandbox:sandbox /home/sandbox/code

USER sandbox

CMD ["node", "/home/sandbox/code/main.js"]
