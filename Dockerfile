FROM python:3.8
ENV PYTHONUNBUFFERED=1


WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install daphne

COPY . /code/

RUN python3 manage.py collectstatic --no-input
EXPOSE 9000
CMD ["daphne", "-b", "0.0.0.0", "-p", "9000", "forge.asgi:application"]