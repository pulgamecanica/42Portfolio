FROM node:16-alpine 

# Set the working directory to /app inside the container
WORKDIR /app

# Copy app files
COPY . /app/

# ==== BUILD =====
# Install dependencies (npm ci makes sure the exact versions in the lockfile gets installed)
RUN npm ci

ENV PORT=3000

# Start the app
CMD [ "npx", "run", "start" ]
