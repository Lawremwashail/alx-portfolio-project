# Use Node.js official image
FROM node:18

# Set work directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all files
COPY . .

# Build the frontend
RUN npm run build

# Expose the app port
EXPOSE 3000

# Serve the app
CMD ["npm", "start"]
