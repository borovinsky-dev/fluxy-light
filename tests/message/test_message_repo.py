from datetime import datetime, timezone
from uuid import uuid4

import pytest

from fluxy_light.database.database import Database
from fluxy_light.models.message import Message
from fluxy_light.repository.message_repo import MessageRepo


@pytest.fixture
def setup_data(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    sender_id = uuid4()
    participant_2_id = uuid4()
    conversation_id = uuid4()

    created_at = datetime.now(timezone.utc).isoformat()

    # Создаём пользователей и диалог,
    # на которые ссылается сообщение.
    with database.get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO users (id, username, role, created_at)
            VALUES (?, ?, ?, ?)
            """,
            [
                (str(sender_id), "sender", "member", created_at),
                (str(participant_2_id), "recipient", "member", created_at),
            ],
        )

        connection.execute(
            """
            INSERT INTO conversations (
                id, participant_1_id, participant_2_id, created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(conversation_id),
                str(sender_id),
                str(participant_2_id),
                created_at,
            ),
        )

    repo = MessageRepo(database)

    return repo, sender_id, conversation_id


def test_save_and_get_message_by_id(setup_data):
    repo, sender_id, conversation_id = setup_data

    message = Message(
        sender_id=sender_id,
        text="Привет!",
        conversation_id=conversation_id,
    )

    repo.save_message(message)

    result = repo.get_message_by_id(message.id)

    assert isinstance(result, Message)
    assert result.id == message.id
    assert result.sender_id == sender_id
    assert result.conversation_id == conversation_id
    assert result.room_id is None
    assert result.text == "Привет!"
    assert result.created_at == message.created_at


def test_get_missing_message_returns_none(setup_data):
    repo, _, _ = setup_data

    result = repo.get_message_by_id(uuid4())

    assert result is None
