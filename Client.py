import sys
import logging
import asyncio
import slixmpp
import getpass

from optparse import OptionParser
from slixmpp.exceptions import IqError, IqTimeout

# basado en los ejemplos de https://sleekxmpp.readthedocs.io/en/latest/index.html

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class RegisterBot(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)

    async def start(self, event):

        self.send_presence()
        await self.get_roster()
        self.disconnect()

    async def register(self, iq):

        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            await resp.send()
            print("Account created for %s!" % self.boundjid)
        except IqError as e:
            print("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()
        self.disconnect()

class Client(slixmpp.ClientXMPP):

    def __init__(self, user, passw):
        slixmpp.ClientXMPP.__init__(self, user, passw)
        #print('algo pasa')
        self.jid = user
        self.password = passw
        self.add_event_handler("session_start", self.start)
        #self.add_event_handler(self.login)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.add_event_handler("changed_status", self.wait_for_presences)

        self.received = set()
        self.presences_received = asyncio.Event()

    def wait_for_presences(self, pres):
        """
        Track how many roster entries have received presence updates.
        """
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()

    async def start(self, event):
        self.send_presence()
        #await self.get_roster()

        access = True
        print('se ha conectado\n')
        print("login Listo\n")
        while access:
            print("elija una de las siguientes opciones: \n1. Mostrar todos los usuarios y su estado \n2. Agregar un usuario a sus contactos \n3. Mostrar detalles de contacto de un usuario \n4. Comunicacion 1 a 1 con algun usuario \n5. participar en conversacion grupal \n6. mensaje de precencia \n7. salir ")
            opcion = input("opcion a elegir es: ")
            if opcion == "1":
                #codigo para mostrar usuarios
                try:
                    await self.get_roster()
                except IqError as err:
                    print('Error: %s' % err.iq['error']['condition'])
                except IqTimeout:
                    print('Error: Request timed out')
                self.send_presence()

                print('Waiting for presence updates...\n')
                await asyncio.sleep(10)

                print('Roster for %s' % self.boundjid.bare)
                groups = self.client_roster.groups()
                for group in groups:
                    print('\n%s' % group)
                    print('-' * 72)
                    for self.jid in groups[group]:
                        sub = self.client_roster[self.jid]['subscription']
                        name = self.client_roster[self.jid]['name']
                        if self.client_roster[self.jid]['name']:
                            print(' %s (%s) [%s]' % (name, self.jid, sub))
                        else:
                            print(' %s [%s]' % (self.jid, sub))

                        connections = self.client_roster.presence(self.jid)
                        for res, pres in connections.items():
                            show = 'available'
                            if pres['show']:
                                show = pres['show']
                            print('   - %s (%s)' % (res, show))
                            if pres['status']:
                                print('       %s' % pres['status'])

                #print("1")
            if opcion == "2":
                #codigo para agregar contanto
                new_friend = (input("user: "))
                xmpp.send_presence_subscription(pto= new_friend + "@redes2020.xyz")
                print("Amigo agregado")
                #print("2")
            if opcion == "3":
                #codigo para mostrar detalles de un contanto
                print("3")
            if opcion == "4":
                #codigo para iniciar conversacion 1 a 1 con otro usuario
                print("4")
            if opcion == "5":
                #codigo para añadirme a un chat grupal
                print("5")
            if opcion == "6":
                #codigo para el mensaje de presencia
                shw = input("Estado(chat, away, xa, dnd): ")
                stts = input("Mensaje: ")
                self.send_presence(pshow= shw, pstatus= stts)
                print("Presence cambiado\n")
            if opcion == "7":
                access = False
                print("entraste")
                break
            if opcion != "1" or opcion != "2" or opcion != "3" or opcion != "4" or opcion != "5" or opcion != "6" or opcion != "7": 
                print("ha escrito mala su eleccion. Por favor, intentelo y sin dejar espacios en blanco")
        print("saliste")
        self.disconnect()

if __name__ == '__main__':
    option = ''
    validated = False

    while option != 'exit':
        print('####     Usuario no identificado     ####')
        print('* "log in": para iniciar sesion con usuario')
        print('* "sign up": para crear un nuevo usuario')
        print('* "sign out": para eliminar usuario del sistema')
        print('* "exit": Para cerrar programa')
        option = input('Que opcion se toma? ')

        if option == 'log in':
            #codigo para iniciar sesion
            userJID = input("userJID: ")
            password = input("password: ")
            username = userJID + "@redes2020.xyz"
            xmpp = Client(username, password)

            if xmpp.connect() == None:
                xmpp.process()
            else:
                print("Unable to connect.")

        if option == 'sign up ':
            userJID = input("userJID: ")
            password = input("password: ")
            username = userJID + "@redes2020.xyz"

            xmpp = RegisterBot(username, password)

            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data forms
            xmpp.register_plugin('xep_0066') # Out-of-band Data
            xmpp.register_plugin('xep_0077') # In-band Registration
            xmpp['xep_0077'].force_registration = True
            xmpp.connect()
            print("Im in boyssssss!")

        if option == 'sign out':
            userJID = input("userJID: ")
            password = input("password: ")

            xmpp = Client(userJID, password)
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data Forms
            xmpp.register_plugin('xep_0060') # PubSub
            xmpp.register_plugin('xep_0199') # XMPP Ping
            if xmpp.connect():
                xmpp.process(block=False)
                xmpp.del_roster_item(userJID + "@redes2020.zxy")
                xmpp.disconnect()
            else:
                print("Bad connect.")

        if option == 'exit':
            print('arrivederci')

