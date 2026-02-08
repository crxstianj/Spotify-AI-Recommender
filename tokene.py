import requests

class SpotifyAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.access_token = None

    def get_token(self):
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(self.token_url, data=data, auth=(self.client_id, self.client_secret))
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            return self.access_token
        else:
            raise Exception(f"Error al obtener token de cliente: {response.status_code}\n{response.text}")

    def get_auth_header(self):
        if not self.access_token:
            self.get_token()
        return {"Authorization": f"Bearer {self.access_token}"}

