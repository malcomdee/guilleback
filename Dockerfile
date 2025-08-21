# front2/Dockerfile
FROM node:20-slim AS build
WORKDIR /web
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:stable-alpine
# Copia el build a nginx
COPY --from=build /web/dist /usr/share/nginx/html
# Exponer puerto que verá Code Engine
EXPOSE 8080
# Nginx escucha 80; redirige el tráfico 8080->80 con variable de entorno de CE:
ENV PORT=8080
CMD ["sh", "-c", "nginx -g 'daemon off;'"]
