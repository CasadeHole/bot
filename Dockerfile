FROM python:alpine

RUN apk --no-cache upgrade
RUN apk add git

RUN pip install --upgrade pip

RUN adduser -D dong
USER dong
WORKDIR /home/dong

RUN pip install --user pipenv
ENV PATH="/home/dong/.local/bin:${PATH}"

COPY --chown=dong:dong ./Pipfile ./Pipfile.lock ./
RUN pipenv install --system

COPY --chown=dong:dong ./ ./

CMD [ "python", "main.py" ]