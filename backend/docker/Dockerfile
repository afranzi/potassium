FROM python:3.12-slim as builder

ENV APP_DIR /opt/potassium
WORKDIR $APP_DIR

COPY uv.lock pyproject.toml README.md $APP_DIR/
COPY potassium potassium

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv sync \
    && uv build  \
    && uv pip install dist/*.whl

FROM python:3.12-slim
LABEL org.opencontainers.image.title="Potassium Backend" \
      org.opencontainers.image.description="The tool to manage Debezium Signalling with precision and elegance" \
      org.opencontainers.image.vendor="Potassium"

ENV APP_DIR /opt/potassium
WORKDIR $APP_DIR
ENV PATH="${APP_DIR}/.venv/bin:${PATH}"
COPY --from=builder ${APP_DIR}/.venv ${APP_DIR}/.venv

RUN adduser --system --group appuser
USER appuser

ENV PATH="${APP_DIR}/.venv/bin:${PATH}"

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
