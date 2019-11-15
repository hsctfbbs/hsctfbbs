FROM python:3.6

RUN pip install flask requests uwsgi Flask-Session Flask-SQLAlchemy

RUN useradd -U -m -d /home/ctfuser ctfuser && \
	chown -R root:root /home/ctfuser

ADD app.py uwsgi.ini flag.txt /home/ctfuser/
ADD db /home/ctfuser/db
ADD templates /home/ctfuser/templates

RUN mkdir /home/ctfuser/__pycache__ && \
	mkdir /home/ctfuser/sessions && \
	chown ctfuser:ctfuser /home/ctfuser/__pycache__ /home/ctfuser/sessions /home/ctfuser/db /home/ctfuser/db/hsctfbbs.db

EXPOSE 13894

USER ctfuser
WORKDIR /home/ctfuser/
CMD ["uwsgi", "--ini", "uwsgi.ini"]
