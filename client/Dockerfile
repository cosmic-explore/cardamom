FROM node:latest

# Set the working directory inside the container
WORKDIR /usr/src/cardamom

# Copy the application files
COPY . .

# Install dependencies
RUN npm install

# Expose the port your app runs on
EXPOSE 5173

# Start the React App
CMD ["npm", "run", "dev", "--", "--host"]