# Stage 1: Build the React application
FROM node:20-alpine AS build-stage

WORKDIR /app

# Copy package configurations and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the application files and build
COPY . .
RUN npm run build

# Stage 2: Serve using Nginx
FROM nginx:stable-alpine AS production-stage

# Copy compiled files from the build stage to Nginx web root
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom Nginx proxy configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
