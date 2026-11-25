import sys
import requests
import json
import traceback

URL = "https://api.dicionario-aberto.net/word/"

def request(palavra: str) -> list[dict]:
    try:
        response = requests.get(URL + palavra)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console_log(f"Erro ao fazer a requisição para a API:\n{traceback.format_exc()}", 3)
        return [{}]


def get_xml_camp(req: list[dict]) -> list[str]:
    listxm = []
    for item in req:
        listxm.append(item["xml"])
    return listxm


def is_substantivo(xml: str) -> bool:
    return "<gramGrp>f." in xml or "<gramGrp>m." in xml


def load_file(file: str) -> str:
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

    
def load_json(file: str) -> dict:
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def check_debug():
    if len(sys.argv) > 1 and sys.argv[1] == "d":
        return True
    return False


def console_log(msg: str, severity: int) -> None:
    debug = check_debug()
    
    severity_strings = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL"
    ]

    if severity == 0 and not debug:
        return

    print(f"[{severity_strings[severity]}] {msg}")

    