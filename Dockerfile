FROM python:3.11.2

WORKDIR /app

COPY requirements.txt ./

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    pip show flask

RUN mkdir model && \
    curl -o model.zip https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip && \
    unzip model.zip -d model && \
    rm model.zip

# RUN curl -o recasepunc.zip https://alphacephei.com/vosk/models/vosk-recasepunc-ru-0.22.zip && \
#     unzip recasepunc.zip -d recasepunc && \
#     rm -rf recasepunc.zip

COPY . .

ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["python", "app.py"]
