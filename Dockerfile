FROM stjepanruklic/crypto-bot-producer-base:1.0.0
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
ARG COINBASE_API_KEY
ENV COINBASE_API_KEY ${COINBASE_API_KEY}
ARG COINBASE_API_SECRET
ENV COINBASE_API_SECRET ${COINBASE_API_SECRET}
EXPOSE 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]