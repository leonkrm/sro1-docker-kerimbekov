# --- Стадия 1: build ---
FROM python:3.12-alpine AS build
WORKDIR /src
COPY tools/ tools/
COPY data/ data/
RUN python tools/build_report.py

# --- Стадия 2: test ---
FROM build AS test
COPY tests/ tests/
RUN python -m unittest discover -s tests -v

# --- Стадия 3: финальная ---
FROM python:3.12-alpine
WORKDIR /medeu-ice
COPY app/server.py .
COPY --from=test /src/out/report.json .
ENV BRANCH="Medeu"
ENV TOP="5"
EXPOSE 8080
CMD ["python", "server.py"]