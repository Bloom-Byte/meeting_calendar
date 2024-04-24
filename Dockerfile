FROM python:3.10.12
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y gettext

RUN pip install --upgrade pip

ENV PATH="/home/user/.local/bin:${PATH}"

WORKDIR /django


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "manage.py", "runserver"]