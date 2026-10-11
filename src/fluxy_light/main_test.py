from fluxy_light.models.conversation import Conversation
from fluxy_light.models.user import User
from fluxy_light.models.message import Message
from fluxy_light.models.room import Room
from fluxy_light.storage.database import Database


def main():
    alice = User("alice")
    bob = User("bob")

    # создание личного диалога
    conversation = Conversation((alice.id, bob.id))

    message = Message(
        sender_id=alice.id,
        text="Привет, Боб!",
        conversation_id=conversation.id,
    )

    room = Room(
        name="General",
        creator_id=alice.id,
        is_moderated=False,
    )

    room_message = Message(
        sender_id=bob.id,
        text="Всем привет!",
        room_id=room.id,
    )

    database = Database()
    connection = database.get_connection()
    print(connection.execute("SELECT sqlite_version()").fetchone())
    connection.close()


if __name__ == "__main__":
    print("Прямой запуск тестового модуля __MAIN__")
    main()
