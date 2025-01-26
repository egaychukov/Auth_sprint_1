import abc
import json
import os
from datetime import datetime
from typing import Any


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def save_state(self, state: dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        """Получить состояние из хранилища."""


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

        if not os.path.exists(self.file_path):
            initial_data = {
                "film_work_modified": str(datetime.min),
                "genre_modified": str(datetime.min),
                "person_modified": str(datetime.min),
            }
            with open(self.file_path, 'w') as storage_json_file:
                json.dump(initial_data, storage_json_file)

    def save_state(self, state: dict[str, Any]) -> None:
        with open(self.file_path, 'r') as storage_json_file:
            data = json.load(storage_json_file)
            data.update(state)

        with open(self.file_path, 'w') as storage_json_file:
            json.dump(data, storage_json_file)

    def retrieve_state(self) -> dict[str, Any]:
        with open(self.file_path, 'r') as storage_json_file:
            data = json.load(storage_json_file)
        return data or {}


class State:
    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        return self.storage.retrieve_state().get(key, None)
