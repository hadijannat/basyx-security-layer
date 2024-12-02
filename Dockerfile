FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY README.md .
COPY basyx_security ./basyx_security

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -r -u 1000 securityuser
USER securityuser

CMD ["python", "-m", "basyx_security"] 