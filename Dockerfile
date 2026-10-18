FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AQRUNTIME_HOME=/app \
    CMAKE_ARGS="-DGGML_BLAS=OFF -DGGML_NATIVE=OFF"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Keep the Cloud Run image focused on the GGUF CPU path; PyTorch is not needed
# for this prototype and would make the image substantially larger.
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir PyYAML typer huggingface_hub llama-cpp-python pypdf

# The quantized Gemma model is fetched during image build, not committed to Git.
RUN python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='bartowski/gemma-2-2b-it-GGUF', filename='gemma-2-2b-it-Q4_K_M.gguf', local_dir='models/bartowski-gemma-2-2b-it-gguf')"

COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
COPY docs/workdoc_demo_sample.md ./docs/workdoc_demo_sample.md

RUN python -m pip install --no-cache-dir --no-deps .

EXPOSE 8080
CMD ["sh", "-c", "exec aq serve --host 0.0.0.0 --port ${PORT:-8080}"]
