import sys
import logging
import asyncio
import slixmpp
import getpass

from optparse import OptionParser
from slixmpp.exceptions import IqError, IqTimeout

# basado en los ejemplos de https://sleekxmpp.readthedocs.io/en/latest/index.html
# para sistemas 32 bti windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#para poder registrar usuarios
class RegisterBot(slixmpp.ClientXMPP):

    #crea usrnm con pswd
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)

    # inicia la precencia en el rooster
    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        self.disconnect()

    # aca se puede ingresa el id para que se quede asociado el registro
    async def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        # aca se pone por errores de servidor cliente
        try:
            await resp.send()
            print("Account: %s!" % self.boundjid)
        except IqError as e:
            print("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()
        self.disconnect()

    # se toma id para quitar pero no se por que no jala
    def del_roster_item(self, jid):
        return self.client_roster.remove(jid)

# conexion con el server
class Client(slixmpp.ClientXMPP):
    # plugins par dar permiso y credenciales
    def __init__(self, user, passw):
        slixmpp.ClientXMPP.__init__(self, user, passw)
        self.jid = user
        self.password = passw
        self.add_event_handler("session_start", self.start)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.add_event_handler("changed_status", self.wait_for_presences)

        self.received = set()
        self.presences_received = asyncio.Event()

    # espera que se haga el update de la precencia
    def wait_for_presences(self, pres):
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()

    # no se donde se pone para borrar esta porqueria
    def del_roster_item(self, jid):
        return self.client_roster.remove(jid)

    # menu con funciones que se van a usar las comentadas no me salieron
    async def start(self, event):
        self.send_presence()
        #await self.get_roster()

        access = True
        print('FULL STEAMS AHEAD CREW!')
        while access:
            print('Bienvenid@!')
            print('users: Mostrar todos los usuarios y su estado')
            print('add: Agregar un usuario a sus contactos')
            print('display: Mensaje de precencia')
            print('exit: salir')

            #print('details: Mostrar detalles de contacto de un usuario')
            #print('chat: Comunicacion 1 a 1 con algun usuario')
            #print('gchat: Conversacion grupal')
            opcion = input('Que opcion se toma? ')

            if opcion == "users":
                #please dont die on me
                try:
                    await self.get_roster()
                except IqError as err:
                    print('Error: %s' % err.iq['error']['condition'])
                except IqTimeout:
                    print('User timed out')

                #updating
                self.send_presence()
                await asyncio.sleep(5)

                # dice quienes estan despues de  time out de 5 seg
                print('My peps for %s' % self.boundjid.bare)
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
            if opcion == "add":
                new_node = (input("user: "))
                username = new_node + "@redes2020.xyz"
                xmpp.send_presence_subscription(pto = username)
                print("New contact added")
            if opcion == "display":
                shw = input("Estado(chat, away, xa, dnd): ")
                stts = input("Status: ")
                self.send_presence(pshow= shw, pstatus= stts)
                print("Display status updated!")
            if opcion == "exit":
                access = False
                break
        print("See you later cowboy!")
        self.disconnect()

if __name__ == '__main__':
    option = ''
    validated = False

    while option != 'exit':
        print('####     Usuario no identificado     ####')
        print('* "log in": para iniciar sesion con usuario')
        print('* "sign up": para crear un nuevo usuario')
        #print('* "sign out": para eliminar usuario del sistema')
        print('* "exit": Para cerrar programa')
        option = input('Que opcion se toma? ')

        if option == 'log in':
            #codigo para iniciar sesion
            userJID = input("userJID: ")
            password = input("password: ")
            username = userJID + "@redes2020.xyz"
            xmpp = Client(username, password)

            # si no hay respues == unable to connec
            if xmpp.connect() == None:
                xmpp.process()
            else:
                print("Unable to connect.")

        if option == 'sign up':
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
            username = userJID + "@redes2020.xyz"

            xmpp = Client(username, password)
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data Forms
            xmpp.register_plugin('xep_0060') # PubSub
            xmpp.register_plugin('xep_0199') # XMPP Ping

            # elif para  saber si se pudo o no
            if xmpp.connect():
                xmpp.process(block=False)
                xmpp.del_roster_item(username)
                xmpp.disconnect()
                print('byebye user forever')
            else:
                print("Bad connect.")

        if option == 'exit':
            print('arrivederci')

