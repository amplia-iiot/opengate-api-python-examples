FROM python:2-onbuild
RUN pip install Flask
RUN pip install requests
ADD . /code
WORKDIR /code
CMD python app.py