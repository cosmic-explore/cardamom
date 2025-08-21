# Build client
FROM node:18 AS build

WORKDIR /app
COPY ./client ./ 
RUN npm install
RUN npm run build  # Outputs to /app/dist

# Add client to nginx and serve it
FROM nginx:alpine

# Install openssl to generate self-signed SSL cert
RUN apk add --no-cache openssl

# Generate self-signed certificate for testing with HTTPS so a paid for domain is not required
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/selfsigned.key \
    -out /etc/ssl/certs/selfsigned.crt \
    -subj "/C=US/ST=Test/L=Test/O=Test/CN=localhost"

# Copy Vite output from build stage to Nginx web root
COPY --from=build /app/dist /usr/share/nginx/html

COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Expose port and run nginx

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]