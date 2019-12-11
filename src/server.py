#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#  Improved by Ilia Parkhomenko
#  parhomych@ya.ru
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
#  Ctrl + Alt + L - форматирование кода
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):
        # Потенциальный баг для внимательных =)
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def send_history(self):
        return self.factory.last_10_messages

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"
            self.factory.last_10_messages.append(content)

            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:
            # login:admin -> admin
            if content.startswith("login:"):
                self.login = content.replace("login:", "")
                if self.login in self.factory.clients:
                    self.sendLine(f"Login {self.login} is busy, try another login".encode())
                    self.connectionLost()
                else:
                    self.sendLine("Welcome!".encode())
                    self.connectionMade()
                    self.send_history()
            else:
                self.sendLine("Invalid login".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    last_10_messages: list

    def startFactory(self):
        self.clients = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
