import requests
import json

URL = "https://api.dicionario-aberto.net/word/"

def request(palavra: str) -> list[dict]:
    try:
        response = requests.get(URL + palavra)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return [{}]


def get_xml_camp(req: list[dict]) -> list[str]:
    listxm = []
    for item in req:
        listxm.append(item["xml"])
    return listxm


def is_substantivo(xml: str) -> bool:
    return "<gramGrp>f." in xml or "<gramGrp>m." in xml


def load_css(file: str) -> str:
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

    
def load_json(file: str) -> dict:
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)