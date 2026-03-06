# Dockerfile for AWS Lambda Python 3.11 with Privacy Features
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first for better caching
COPY requirements-lambda.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-lambda.txt

# Copy application code (entire src directory structure)
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Copy data folder (for CSV fallback)
COPY data/mandi_prices/Agriculture_price_dataset.csv ${LAMBDA_TASK_ROOT}/data/mandi_prices/Agriculture_price_dataset.csv

# Set environment variables
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}:${LAMBDA_TASK_ROOT}/src"
ENV LOG_LEVEL="INFO"

# Lambda handler - points to src/aws/lambda_handler.py::lambda_handler
CMD ["src.aws.lambda_handler.lambda_handler"]
