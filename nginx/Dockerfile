FROM nginx
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/staticfiles
COPY nginx.conf /etc/nginx/conf.d

WORKDIR $APP_HOME
