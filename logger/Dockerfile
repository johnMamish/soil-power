FROM python:3.11.9-slim-bullseye@sha256:98d223d4801f1237560234274e23f7ed8571bdd5988879d37e5a1ff5f5764ecb
WORKDIR /logger
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD sleep infinity
