from abc import ABC, abstractmethod

from fastapi import UploadFile


class StorageService(ABC):
    @abstractmethod
    def put(self, file: UploadFile, key: str) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass
