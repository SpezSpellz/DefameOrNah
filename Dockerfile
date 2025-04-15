FROM alpine:edge
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache libstdc++ python3-dev libgomp go build-base git python3 py3-pip
RUN ln -sf python3 /usr/bin/python
RUN git clone https://github.com/ollama/ollama.git
RUN cd ollama && git checkout v0.6.5 && eval $(go env) && go generate . && go build . && cp ollama /usr/bin/ollama && rm -rf ollama
RUN ollama serve & (sleep 5; ollama pull bge-m3)
COPY . .
RUN pip install --break-system-packages -r requirements.txt
RUN fastapi-codegen --input ./openapi/api.yml --output ./stub --output-model-type pydantic_v2.BaseModel --template-dir ./templates
RUN echo MODEL_PATH=./analytics/model.joblib >> .env
RUN echo DATA_PATH=./analytics/data.csv >> .env
RUN apk del python3-dev build-base go git
RUN apk -v cache clean
ENV OLLAMA_HOST=127.0.0.1
CMD [ "sh","start.sh" ]