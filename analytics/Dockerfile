FROM python:3.12-slim
WORKDIR /app
RUN groupadd --gid 10001 zone1 && useradd --uid 10001 --gid zone1 --no-create-home zone1 \
    && mkdir -p /var/lib/zone1 && chown zone1:zone1 /var/lib/zone1
COPY analytics/__init__.py analytics/collector.py ./analytics/
COPY data/analytics-plan.json data/products.json data/articles.json ./data/
USER 10001:10001
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    ZONE1_ANALYTICS_BIND=0.0.0.0 ZONE1_ANALYTICS_PORT=8078 \
    ZONE1_ANALYTICS_DB_PATH=/var/lib/zone1/events.sqlite3
EXPOSE 8078
# Defaults remain fail-closed. Explicit deployment/privacy/origin evidence is required.
CMD ["python3", "-m", "analytics.collector"]
