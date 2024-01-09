
import time
from typing import Protocol, Self
from pydantic import BaseModel

class ConsumerEmptySpaMessage(BaseModel):
    """
    Defines the message for SPA applications
    """
    # ClientId: str | None = None
    # ClientName: str | None = None
    # Topic: str
    # ResponseTopic: str | None = None
    # ContentType: str | None = None
    Payload: str
    # QOS: int = 2
    # Content: str | None = None

class ConsumerMinimumSpaMessage(BaseModel):
    Payload: str | None = None
    Topic: str | None = None
    ResponseTopic: str | None = None


class ConsumerRequestSpaMessage(BaseModel):
    """
    Defines the message for SPA applications
    """
    ClientId: str | None = None
    ClientName: str | None = None
    Topic: str
    ResponseTopic: str | None = None
    ContentType: str | None = None
    Payload: str | None = None
    QOS: int = 2
    Content: str | None = None


class ConsumerResponseSpaMessage(BaseModel):
    """
    Defines the message for SPA applications
    """
    client_id: str | None = None
    client_name: str | None = None
    topic: str
    response_topic: str | None = None
    content_type: str | None = None
    payload: bytes
    qos: int
    content: str | None = None
#    timestamp: int = int(time.time())