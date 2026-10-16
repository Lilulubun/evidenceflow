FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EVIDENCEFLOW_HOST=0.0.0.0 \
    EVIDENCEFLOW_PORT=8000 \
    EVIDENCEFLOW_STATE_FILE=/data/runtime_state.json \
    EVIDENCEFLOW_AI_SETTINGS_FILE=/data/runtime_ai_settings.json

WORKDIR /app
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app \
    && mkdir /data && chown app:app /data && chmod 700 /data
COPY server.py app_core.py governance.py ai_adapter.py settings_store.py query_layer.py employee_graph.py evidence.json tkt3_results.json ./
COPY static/ ./static/
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"
CMD ["python", "server.py"]
