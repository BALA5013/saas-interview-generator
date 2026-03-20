# Build step logic: for a simple dev/demo environment using docker-compose, 
# we can use node image and start the dev server directly.

FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
# Using legacy-peer-deps to avoid any react-scripts resolution issues
RUN npm install --legacy-peer-deps

# Copy project files
COPY . .

# Expose the standard React port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
