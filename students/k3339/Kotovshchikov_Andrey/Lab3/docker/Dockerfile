FROM python:3.13-slim AS build

ARG PROJECT=app

WORKDIR /${PROJECT}

COPY ./${PROJECT}/poetry.lock ./${PROJECT}/pyproject.toml /${PROJECT}

RUN apt-get update && \
    apt-get install \
    -y libpq-dev gcc && \
    pip install --upgrade pip && \
    pip install --upgrade wheel && \
    pip install poetry --no-cache-dir && \
    poetry self add poetry-plugin-export && \
    poetry export -o requirements.txt && \
    pip wheel \
    --no-deps \
    --no-cache-dir \
    --wheel-dir /${PROJECT}/wheels \
    -r requirements.txt


FROM python:3.13-slim AS run

ARG PROJECT=app

WORKDIR /${PROJECT}

COPY --from=build /${PROJECT}/wheels /${PROJECT}/wheels
COPY --from=build /${PROJECT}/requirements.txt .

RUN pip install --upgrade pip && \
    pip install \
    --no-cache-dir \
    --no-deps \
    --no-index \
    --find-links=/${PROJECT}/wheels \
    -r requirements.txt

COPY ./${PROJECT} .

CMD [ "/bin/bash" ]
