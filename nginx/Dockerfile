# Build client
FROM node:18 AS build

WORKDIR /app
COPY ./client ./
RUN npm install
RUN npm run build  # Outputs to /app/dist

# Add client to nginx and serve it
FROM nginx:alpine

# Copy Vite output from build stage to Nginx web root
COPY --from=build /app/dist /usr/share/nginx/html

COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Expose port and run nginx

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]