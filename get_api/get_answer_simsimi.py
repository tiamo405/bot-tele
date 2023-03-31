# -*- coding: utf-8 -*-

import requests

def get_answer_simsimi(quess) :
    url = 'https://api.simsimi.vn/v1/simtalk'
    data = {'text': quess, 'lc': 'vn'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, headers=headers, data=data)

    return response