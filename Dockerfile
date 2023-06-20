# for zeabur

FROM python:3.9.17-alpine3.18

LABEL maintainer="Ray"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

RUN alembic upgrade head

EXPOSE 80/tcp
EXPOSE 80/udp

CMD ["uvicorn", "watchlist.main:app", "--host", "0.0.0.0", "--port", "80"]
