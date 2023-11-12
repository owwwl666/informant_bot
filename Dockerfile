FROM python:3.10-alpine3.18

WORKDIR /informant_bot

COPY requirements.txt requirements.txt

RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt

COPY script.py script.py

ENTRYPOINT ["python3", "script.py","--chat_id"]