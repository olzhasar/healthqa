FROM node:latest as build

WORKDIR /frontend

COPY ./frontend/yarn.lock ./frontend/package.json /frontend/
RUN yarn

COPY ./frontend/src /frontend/src
COPY ./frontend/*.js /frontend/
COPY ./backend /backend

RUN yarn run build:prod

FROM nginx:1.21.1-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/conf.d
COPY --from=build /frontend/dist ./usr/share/nginx/static
