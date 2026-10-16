from uuid import uuid4

import pytest

from fluxy_light.models.user import User
from fluxy_light.models.conversation import Conversation
from fluxy_light.models.message import Message
from fluxy_light.models.room import Room

from fluxy_light.repository.user_repo import UserRepo
from fluxy_light.repository.conversation_repo import ConversationRepo
from fluxy_light.repository.message_repo import MessageRepo
from fluxy_light.repository.room_repo import RoomRepo


def test_full_message_flow(database):
    # 1. Создаём репозитории
    user_repo = UserRepo(database)
    conversation_repo = ConversationRepo(database)
    message_repo = MessageRepo(database)
    room_repo = RoomRepo(database)

    # 2. Создаём двух пользователей и сохраняем их
    alice = User(username="alice")
    bob = User(username="bob")

    user_repo.save_user(alice)
    user_repo.save_user(bob)

    assert user_repo.get_by_id(alice.id) is not None
    assert user_repo.get_by_id(bob.id) is not None

    # 3. Создаём личную переписку между Alice и Bob
    conversation = Conversation((alice.id, bob.id))
    conversation_repo.save_conversation(conversation)

    saved_conversation = conversation_repo.get_between_users(alice.id, bob.id)

    assert saved_conversation is not None
    assert saved_conversation.id == conversation.id

    # 4. Alice отправляет личное сообщение Bob
    private_message = Message(
        sender_id=alice.id,
        text="Привет, Bob!",
        conversation_id=conversation.id,
    )
    message_repo.save_message(private_message)

    # 5. Bob отвечает в той же переписке
    reply = Message(
        sender_id=bob.id,
        text="Привет, Alice!",
        conversation_id=conversation.id,
    )
    message_repo.save_message(reply)

    # 6. Получаем личные сообщения из базы
    private_messages = message_repo.get_messages_by_conversation_id(conversation.id)

    assert len(private_messages) == 2
    assert {message.id for message in private_messages} == {
        private_message.id,
        reply.id,
    }
    assert all(
        message.conversation_id == conversation.id and message.room_id is None
        for message in private_messages
    )

    # 7. Создаём комнату, владельцем которой является Alice
    room = Room(
        name="general",
        creator_id=alice.id,
        is_moderated=True,
    )
    room_repo.save_room(room)

    saved_room = room_repo.get_by_id(room.id)

    assert saved_room is not None
    assert saved_room.name == "general"
    assert saved_room.creator_id == alice.id
    assert saved_room.is_moderated is True

    # 8. Alice отправляет сообщение в комнату
    room_message = Message(
        sender_id=alice.id,
        text="Всем привет!",
        room_id=room.id,
    )
    message_repo.save_message(room_message)

    # 9. Bob тоже отправляет сообщение в комнату
    room_reply = Message(
        sender_id=bob.id,
        text="Всем привет!",
        room_id=room.id,
    )
    message_repo.save_message(room_reply)

    # 10. Проверяем сообщения комнаты
    room_messages = message_repo.get_messages_by_room_id(room.id)

    assert len(room_messages) == 2
    assert {message.id for message in room_messages} == {
        room_message.id,
        room_reply.id,
    }
    assert all(
        message.room_id == room.id and message.conversation_id is None
        for message in room_messages
    )

    # 11. Личные сообщения не должны попасть в комнату
    assert not (
        {message.id for message in private_messages}
        & {message.id for message in room_messages}
    )

    # 12. Проверяем получение сообщения по ID
    restored_message = message_repo.get_message_by_id(private_message.id)

    assert restored_message is not None
    assert restored_message.id == private_message.id
    assert restored_message.sender_id == alice.id
    assert restored_message.text == "Привет, Bob!"
    assert restored_message.conversation_id == conversation.id
    assert restored_message.room_id is None

    # 13. Несуществующие объекты не должны находиться
    assert user_repo.get_by_id(uuid4()) is None
    assert conversation_repo.get_by_id(uuid4()) is None
    assert room_repo.get_by_id(uuid4()) is None
    assert message_repo.get_message_by_id(uuid4()) is None


def test_message_requires_exactly_one_destination(users):
    alice, bob = users

    # Нельзя создать сообщение без личной переписки и без комнаты.
    with pytest.raises(ValueError):
        Message(
            sender_id=alice.id,
            text="Некорректное сообщение",
        )

    # Нельзя одновременно указать личную переписку и комнату.
    conversation = Conversation((alice.id, bob.id))
    room = Room("general", alice.id, False)

    with pytest.raises(ValueError):
        Message(
            sender_id=alice.id,
            text="Некорректное сообщение",
            conversation_id=conversation.id,
            room_id=room.id,
        )
