# 1. Start from an official Python image.
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install uv
RUN pip install uv

# 4. Copy dependency files first
COPY pyproject.toml uv.lock ./

# 5. Install dependencies
RUN uv sync --no-dev

# 6. Copy the rest of your application code
COPY . .

# 7. Tell Docker the app listens on port 8000
EXPOSE 8000

# 8. The command to run when the container starts
CMD ["uv", "run", "fastap", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]