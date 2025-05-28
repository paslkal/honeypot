FROM python:slim

RUN apt-get update && \
    apt-get install -y supervisor \
    redis-server

    
WORKDIR /app
    
RUN mkdir -p /app/redis/data
 
COPY requirements.txt /app/

RUN pip install --no-cache -r requirements.txt

COPY . .

CMD ["/usr/bin/supervisord"]