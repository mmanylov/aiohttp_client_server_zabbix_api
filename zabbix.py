from aiohttp import ClientSession

ZABBIX_URLS = [
    'http://0.0.0.0:1080/api_jsonrpc.php',
    # 'http://0.0.0.0:2080/api_jsonrpc.php',
]

ZABBIX_STANDARD_AUTH = {
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "user": "Admin",
        "password": "zabbix"
    },
    "id": 1
}


def get_zabbix_hosts_get_payload(auth_token):
    return {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "name"],
            "selectInterfaces": ["interfaceid", "ip"]
        },
        "auth": auth_token,
        "id": 2
    }


def get_zabbix_host_groups_payload(auth_token):
    return {
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {
            "output": "extend",
        },
        "auth": auth_token,
        "id": 3
    }


class ZabbixClient:
    auth_token = None
    server_url = None

    def __init__(self, server_url):
        self.server_url = server_url

    async def call_api(self, json_payload):
        async with ClientSession() as session:
            async with session.post(self.server_url, json=json_payload) as resp:
                resp = await resp.json()
                error = resp.get('error')
                if error:
                    raise Exception(error.get('message'), error.get('data'))
                return resp.get('result')

    async def authorize(self):
        token = await self.call_api(ZABBIX_STANDARD_AUTH)
        if token:
            self.auth_token = token

    async def get_hosts(self):
        hosts = list()
        result = await self.call_api(get_zabbix_hosts_get_payload(self.auth_token))
        for host in result:
            host_data = {
                'hostid': host.get('hostid'),
                'host': host.get('host'),
                'name': host.get('name'),
            }

            interfaces = host.get('interfaces')
            ips = list()
            for interface in interfaces:
                ips.append(interface.get('ip'))

            host_data['ips'] = ips
            hosts.append(host_data)

        return hosts

    async def get_host_groups(self):
        return await self.call_api(get_zabbix_host_groups_payload(self.auth_token))


async def get_duplicate_hosts(hosts):
    # TODO: process hosts array for matching names or ips
    return hosts


async def get_zabbix_clients():
    clients = list()
    for url in ZABBIX_URLS:
        client = ZabbixClient(url)
        await client.authorize()
        clients.append(client)

    return clients