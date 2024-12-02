# Use Node.js as the base image
FROM node:18

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json /app/

# Install dependencies
RUN npm install

# Globally install required packages
RUN npm install -g @expo/ngrok@^4.1.0

# Copy the remaining application files
COPY . /app

# Expose the default Expo ports
EXPOSE 19000
EXPOSE 8081

# Run Expo
CMD ["npx", "expo", "start"]
