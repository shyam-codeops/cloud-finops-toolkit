FROM python:3.11-slim

WORKDIR /app

RUN groupadd -g 10001 finops && \
    useradd -u 10001 -g finops -m finops

COPY . .

ENV PYTHONUNBUFFERED=1

USER finops

ENTRYPOINT ["python", "-m", "finops_toolkit.cli"]
CMD ["summary"]
