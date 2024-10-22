FROM python:3.8-slim-bullseye@sha256:0ab344fd043963d5c1d6827143ccee923d0e826f5059a507ac095061ce09bcae
WORKDIR /logger
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y build-essential
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN bash gen_config.sh 'PIS("Teros", 60, fadapter("Teros File", TerosArduino("Teros Group 1"), "data/exp1-teros.log"))' 'PIS("PCB", 60, fadapter("PCB File", PCB("PCB Group 1"), "data/exp1-pcb.log"))'
CMD python main.py
