from fluxy_light.models.conversation import Conversation
from fluxy_light.models.user import User


def main():
    alice = User("alice")
    bob = User("bob")
    c = Conversation((alice.id, bob.id))
    print(c.ids)
    print(c.created_at)
    print(c)


if __name__ == "__main__":
    print("Прямой запуск тестового модуля __MAIN__")
    main()
