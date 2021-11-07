# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:2.7

EXPOSE 3111

# Install pip requirements
COPY ./techtrends/requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY ./project/techtrends /app
RUN python init_db.py

CMD [ "python","app.py" ]

