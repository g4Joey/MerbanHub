# Use official Node.js image as the base
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package.json ./
COPY yarn.lock* package-lock.json* ./

# Install dependencies
RUN npm install 

# Copy rest of the application code
COPY . .

# Expose port 3000
EXPOSE 3000

# Start Next.js app in development mode
CMD ["npm", "run", "dev"]
