FROM python:3.13-slim as builder

RUN pip install uv

WORKDIR /src

COPY pyproject.toml .

RUN uv venv && uv sync --no-cache

FROM python:3.13-slim

WORKDIR /src

COPY --from=builder /src/.venv .venv

COPY . .

CMD ["/src/.venv/bin/python", "-m", "reminder_bot"]