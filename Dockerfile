FROM continuumio/miniconda3:latest

# Install gcc and nodejs/npm for PM2
RUN apt-get update && apt-get install -y gcc nodejs npm && rm -rf /var/lib/apt/lists/*

# Install PM2 globally
RUN npm install -g pm2

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create conda environment
RUN conda env create -f conda_env.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "three-gen-get-prompts", "/bin/bash", "-c"]

# Expose port
EXPOSE 4001

# Run the application with PM2
CMD ["pm2-runtime", "start", "three-gen-get-prompts.config.js"]