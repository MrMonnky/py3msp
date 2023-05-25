from AsyncClient import AsyncClient
from amfResult import Result as amfResult
from amfDescription import Description as amfDescription
from loginResult import Result as loginResult
from autographResult import Result as autographResult
from authorization import CalculateChecksum
from histogram import GenerateHistogram
from ticketMap import check
from mspsocket import MspSocketUser



async def main():
    # Erstellen Sie eine Instanz Ihres AsyncClients
    client = AsyncClient()

    # Setzen Sie Ihre Anmeldeinformationen und den gewünschten Server
    username = 'Sisi08'
    password = 'msp123'
    server = 'DE'

    try:
        # Melden Sie sich an
        await client.login_async(username, password, server)
        print('Anmeldung erfolgreich!')

        # Geben Sie ein Autogramm an einen bestimmten Benutzernamen
        target_username = 'TargetUsername'
        await client.give_autograph_async(client.actor_id, target_username)
        print('Autogramm erfolgreich vergeben!')

    except Exception as e:
        print(f'Fehler aufgetreten: {str(e)}')

# Führen Sie die Hauptfunktion aus
asyncio.run(main())
