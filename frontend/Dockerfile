# Stage 1: Build the React/Vite application
FROM node:22-alpine as builder

# Set working directory
WORKDIR /app

# Install dependencies first (for better caching)
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# We allow passing VITE_API_URL as a build argument so it gets baked into the static files!
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the production static files
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:alpine

# Copy our custom Nginx configuration to handle React Router correctly
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app from the builder stage into Nginx's hosting folder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 for traffic
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
