# Build stage
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production server stage
FROM nginx:alpine

# Copy built assets to Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Custom nginx config to handle React Router if needed
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
