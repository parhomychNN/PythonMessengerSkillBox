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
        for message in self.factory.last_10_messages:
            self.sendLine(message.encode())

    def lineReceived(self, line: bytes):
        content = line.decode(errors="ignore")

        if self.login is None:
            # login:admin -> admin
            if content.startswith("login:"):
                self.login = content.replace("login:", "")
                if self.factory.clients.__contains__(self.login):
                    self.sendLine(f"Login {self.login} is busy, try another login".encode())
                    self.connectionLost()
                else:
                    self.sendLine("Welcome!".encode())
                    self.connectionMade()
                    self.send_history()
            else:
                self.sendLine("Invalid login".encode())

            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:
            content = f"Message from {self.login}: {content}"
            self.factory.last_10_messages.append(content)


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    last_10_messages: list

    def startFactory(self):
        self.clients = []
        self.last_10_messages = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
