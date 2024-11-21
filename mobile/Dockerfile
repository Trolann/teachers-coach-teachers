# Use Node.js as the base image
FROM node:18

# Set working directory
WORKDIR /app

# Copy the Expo app files
COPY package.json package-lock.json /app/
COPY . /app

# Install dependencies
RUN npm install

RUN npm install -g @expo/ngrok@^4.1.0


# Expose the default Expo ports
EXPOSE 19000
EXPOSE 8081

# Run Expo
CMD ["npx", "expo", "start"]

