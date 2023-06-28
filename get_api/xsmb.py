import requests


def xsmb():
    url = "https://api-xsmb.cyclic.app/api/v1"
    response = requests.get(url)
    results = response.json()
    time = results['time']
    txt = 'xsmb '
    txt += time + '\n'
    for key in results['results']:
        txt+= (key + ': ')
        for i in results['results'][key]:
            txt+= (i + ' ')
        txt += '\n'
    return txt
xsmb()

