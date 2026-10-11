from fluxy_light.models.user import User
from fluxy_light.models.conversation import Conversation
from fluxy_light.models.message import Message
from fluxy_light.models.room import Room


def test_personal_conversation_messaging():
    # Создаём двух пользователей
    alice = User("alice")
    bob = User("bob")

    # Создаём личную переписку
    conversation = Conversation((alice.id, bob.id))

    # Алиса отправляет сообщение
    first_message = Message(
        sender_id=alice.id,
        text="Привет, Боб!",
        conversation_id=conversation.id,
    )

    # Боб отвечает
    second_message = Message(
        sender_id=bob.id,
        text="Привет, Алиса!",
        conversation_id=conversation.id,
    )

    # Проверяем связь пользователей с перепиской
    assert alice.id in conversation.ids
    assert bob.id in conversation.ids

    # Проверяем отправителей и принадлежность сообщений
    assert first_message.sender_id == alice.id
    assert second_message.sender_id == bob.id

    assert first_message.conversation_id == conversation.id
    assert second_message.conversation_id == conversation.id

    # Проверяем уникальность идентификаторов сообщений
    assert first_message.id != second_message.id


def test_room_messaging():
    # Создаём пользователей
    alice = User("alice")
    bob = User("bob")

    # Алиса создаёт комнату
    room = Room(
        name="General",
        creator_id=alice.id,
        is_moderated=False,
    )

    # Боб отправляет сообщение в комнату
    message = Message(
        sender_id=bob.id,
        text="Всем привет!",
        room_id=room.id,
    )

    # Проверяем связи
    assert room.creator_id == alice.id
    assert message.sender_id == bob.id
    assert message.room_id == room.id
    assert message.conversation_id is None


def test_message_accepts_unknown_sender():
    unknown_id = User("alice").id

    # Пока проверяем только поведение модели.
    message = Message(
        sender_id=unknown_id,
        text="Привет",
        room_id=__import__("uuid").uuid4(),
    )

    assert message.sender_id == unknown_id
