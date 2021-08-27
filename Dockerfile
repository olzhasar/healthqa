FROM node:16 as build

WORKDIR /frontend

COPY ./frontend/yarn.lock ./frontend/package.json /frontend/
RUN yarn

COPY ./frontend/src /frontend/src
COPY ./frontend/*.js /frontend/
COPY ./backend /backend

RUN yarn run build:prod
RUN yarn run build-tailwind:prod

FROM nginx:1.21.1-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=build /frontend/dist ./usr/share/nginx/static
