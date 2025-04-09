import joblib
from ollama import AsyncClient
import pandas as pd

model = joblib.load("../analytics/random_forest.joblib")
data_combined = pd.read_csv("../analytics/data_combined.csv")
message_log = open("messages.txt", "a")

from stub.models import (
    DefamationInferenceResponse,
    Error,
    MessageLengthsFrequencyMaxLengthGetResponse,
    WordFrequencyEntry,
    WordFrequenciesGetResponse,
    MessageLengthFrequencyEntry
)

async def check_message(message: str) -> DefamationInferenceResponse:
    """API to check whether message is defamation or not"""
    message_log.write(message.replace("\n", "").replace("\r", "") + "\n")
    message_log.flush()
    embeddings = (await AsyncClient().embed(model="bge-m3", input=[message]))["embeddings"]
    result = model.predict(embeddings)
    return DefamationInferenceResponse(defamation=result[0])

async def word_frequencies() -> WordFrequenciesGetResponse:
    """Retrieve word frequencies"""
    frequencies = dict()
    for msg in data_combined["Message"]:
        for word in msg.split():
            frequencies[word] = frequencies.get(word, 0) + 1
    return WordFrequenciesGetResponse(root=list(map(lambda x: WordFrequencyEntry(text=x[0], value=x[1]), frequencies.items())))

async def message_lengths_frequency(max_length: int) -> MessageLengthsFrequencyMaxLengthGetResponse:
    """Retrieve word lengths"""
    response = list()
    lengths = data_combined["Message"].map(len)
    for i in range(1, 1 + max_length):
        response.append(MessageLengthFrequencyEntry(length=i, frequency=sum(lengths == i)))
    return MessageLengthsFrequencyMaxLengthGetResponse(response)
