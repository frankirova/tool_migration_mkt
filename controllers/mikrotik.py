import routeros_api
from fastapi import HTTPException
import os
from dotenv import load_dotenv
import ipaddress


async def connect_to_mikrotik(data):
    try:
        IP_MIKROTIK = data.get('IP_MIKROTIK')
        load_dotenv()
        PASS_MIKROTIK = os.getenv('PASS_MIKROTIK')
        USER_MIKROTIK = os.getenv('USER_MIKROTIK')
    # conexion con la api Miktoik
        connection = routeros_api.RouterOsApiPool(IP_MIKROTIK, username=USER_MIKROTIK, password=PASS_MIKROTIK, plaintext_login=True)
        api = connection.get_api()
        return api
    except Exception as e:
        # Manejo de la excepción
        print("Ocurrió un error:", str(e))
        raise HTTPException(status_code=500, detail='Error en mikrotik')

async def get_fidelis_addr(api):
    response = api.get_resource("/ip/address").get()
    return [ip for ip in response if 'comment' in ip and 'FIDEL' in ip['comment'].upper()]

async def get_queues(api):
    response = api.get_resource('/queue/simple').get()
    return [objeto for objeto in response if 'name' in objeto and 'FIDEL' in objeto['name'].upper()]

async def get_firewall_addr_list(api):
    response = api.get_resource('/ip/firewall/address-list').get()
    return [objeto for objeto in response if 'comment' in objeto and 'FIDEL' in objeto['comment'].upper()]

async def add_addr_in_mkt_test(api, resultado_filtrado):
    com = api.get_resource("/ip/address")
    for ip_data in resultado_filtrado:
        item = {'address': ip_data['address'], 'network': ip_data['network'], 'interface': 'ether5', 'disabled': ip_data['disabled'], 'comment': ip_data['comment']}
        com.add(**item)

async def add_queue_in_mkt_test(api, queue_list):
    com = api.get_resource("/queue/simple")
    for ip_data in queue_list:
        item = {'name': ip_data['name'], 'target': ip_data['target'], 'max-limit': ip_data['max-limit'], 'burst-limit': ip_data['burst-limit'], 'burst-threshold': ip_data['burst-threshold'], 'burst-time': ip_data['burst-time']}
        com.add(**item)

async def add_firewall_addr_list_in_mkt_test(api, firewall_addr_list_filtered):
    com = api.get_resource('/ip/firewall/address-list')
    for ip_data in firewall_addr_list_filtered:
        item = {'address': ip_data['address'], 'comment': ip_data['comment'], 'list': ip_data['list']}
        com.add(**item)

async def add_comment_addr(array, api):
    new_comment = ' *PASADO A FIDELIS 255.16* '
    for client in array:
        item = {'id': client['id'], 'comment':  new_comment + client['comment']}
        com = api.get_resource("/ip/address")
        com.set(**item)

async def add_comment_firewall_addr_list(array, api):
    new_comment = ' *PASADO A FIDELIS 255.16* '
    for client in array:
        item = {'id': client['id'], 'comment': new_comment + client['comment']}
        com = api.get_resource("/ip/firewall/address-list")
        com.set(**item)

async def add_name(array, api):
    new_name = ' *PASADO A FIDELIS 255.16* '
    for client in array:
        item = {'id': client['id'], 'name': new_name + client['name']}
        com = api.get_resource("/queue/simple")
        com.set(**item)

async def disabled_addr_in_mkt(array, api):
    # new_state = 'true'
    for client in array:
        item = {'id': client['id'], 'disabled': 'true'}
        com = api.get_resource("/ip/address")
        com.set(**item)

async def sorted_queues(queue_list):
    def get_target_value(queue):
        try:
            return ipaddress.IPv4Network(queue['target'])
        except ipaddress.AddressValueError:
            # Si hay un error con la dirección IP, devolvemos un valor alto
            # para que queden al final de la lista
            return ipaddress.IPv4Network('255.255.255.255/32')

    queue_list_sorted = sorted(queue_list, key=get_target_value)
    queue_list_sorted_100 = queue_list_sorted[-100:]
    return queue_list_sorted_100

async def sorted_firewall_addr_list(firewall_addr_list):
    proxyok = [objeto for objeto in firewall_addr_list if objeto.get('list') == 'proxyok']
    def get_addr_value(addr):
        try:
            return ipaddress.IPv4Network(addr['address'])
        except ipaddress.AddressValueError:
            # Si hay un error con la dirección IP, devolvemos un valor alto
            # para que queden al final de la lista
            return ipaddress.IPv4Network('255.255.255.255/32')

    firewall_addr_list_sorted = sorted(proxyok, key=get_addr_value)
    firewall_addr_list_sorted_100 = firewall_addr_list_sorted[-100:]
    return firewall_addr_list_sorted_100

async def add_suspense_addr_list(api, array, array1):
    suspended = [objeto for objeto in array if objeto.get('list') == 'suspendido']
    # suspended_true = [objeto for objeto in suspended if objeto.get('disabled') == 'true']
    def get_addr_value(addr):
        try:
            return ipaddress.IPv4Network(addr['address'])
        except ipaddress.AddressValueError:
            # Si hay un error con la dirección IP, devolvemos un valor alto
            # para que queden al final de la lista
            return ipaddress.IPv4Network('255.255.255.255/32')
    firewall_addr_list_sorted = sorted(suspended, key=get_addr_value)
    firewall_addr_list_sorted_100 = firewall_addr_list_sorted[-100:]
    for item in firewall_addr_list_sorted_100:
        for item1 in array1:
            if item['address'] == item1['address']:
                api.get_resource("/ip/firewall/address-list").add(address=item['address'], list='SUSPENDIDOS', comment=item['comment'], disabled=item['disabled'])

