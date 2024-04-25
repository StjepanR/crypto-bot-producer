FROM python:3.9.18-slim-bullseye
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN --mount=type=secret,id=COINBASE_API_KEY \
    sed -i "s/COINBASE_API_KEY=/COINBASE_API_KEY=$(cat /run/secrets/COINBASE_API_KEY)/".env.production
RUN --mount=type=secret,id=COINBASE_API_SECRET \
    sed -i "s/COINBASE_API_SECRET=/COINBASE_API_SECRET=$(cat /run/secrets/COINBASE_API_SECRET)/".env.production
EXPOSE 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]