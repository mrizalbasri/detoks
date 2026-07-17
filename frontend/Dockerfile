FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy source files
COPY . .

# Expose SvelteKit dev port
EXPOSE 5173

# Run in dev mode (fully compatible with local environment)
CMD ["npm", "run", "dev", "--", "--host"]
