import random

import requests
import time
import json


def t_c(data, method):
    try:
        return data[method]
    except Exception:
        return '-'


def RuCaptcha(site_key, url, key, action, proxy_use):
    if True:
        r = requests.post('https://rucaptcha.com/in.php', json={"key": key,
                                                                "method": 'userrecaptcha',
                                                                'version': 'v3',
                                                                'action': action,
                                                                'min_score': '3',
                                                                'googlekey': site_key,
                                                                'pageurl': url,
                                                                'json': 1,
                                                                'proxy': f'{proxy_use[1]}@{proxy_use[0]}'
                                                                })

        r = json.loads(r.text)
        print('Создано задание № ' + str(r['request']) + '.')
        taskId = r['request']
        for i in range(12):
            time.sleep(10)
            r = requests.post(f'https://rucaptcha.com/res.php?key={key}&action=get&json=1&id={taskId}')
            r = json.loads(r.text)
            if r['request'] != 'CAPCHA_NOT_READY':
                if r['status'] == 1:
                    return r['request']
                print(r, 'error')
                return 'Error'


def get_check_auto_history(data):
    owners = 'Периоды владения транспортным средством:\n'
    for i in data['RequestResult']['ownershipPeriods']['ownershipPeriod']:
        date_from = i['from'][8:10] + '.' + i['from'][5:7] + '.' + i['from'][0:4]
        try:
            date_to = ' по ' + i['to'][8:10] + '.' + i['to'][5:7] + '.' + i['to'][0:4]
        except Exception:
            date_to = ''
        if i['simplePersonType'] == 'Natural':
            face = 'Физическое лицо'
        elif i['simplePersonType'] == 'Legal':
            face = 'Юридическое лицо'
        owners += 'c ' + date_from + date_to + ': ' + face + '\n'
    v_i = data['RequestResult']['vehicle']
    v_pi = data['RequestResult']['vehiclePassport']

    vehicle_info_text = f"Марка и(или) модель: {t_c(v_i, 'model')}\nГод выпуска: {t_c(v_i, 'year')}\n" \
                        f"Идентификационный номер (VIN): {t_c(v_i, 'vin')}\n" \
                        f"Номер кузова (кабины): {t_c(v_i, 'bodyNumber')}\nЦвет кузова (кабины): {t_c(v_i, 'color')}\n" \
                        f"Рабочий объем (см³): {t_c(v_i, 'engineVolume')}\nМощность (кВт/л.с.): {t_c(v_i, 'powerKwt')}/" \
                        f"{t_c(v_i, 'powerHp')}\nТип транспортного средства: Категория {t_c(v_i, 'category')}\n" \
                        f"Номер двигателя: {t_c(v_i, 'engineNumber')}\nНомер информации с данными: {t_c(v_pi, 'number')}\n" \
                        f"Данные: {t_c(v_pi, 'issue')}\n\n{owners}\n"

    return vehicle_info_text


def get_check_auto_limits(data):
    return '\n\nНайдено ограничений: ' + str(data['RequestResult']['count']) + '.'


def get_dtp_data(data):
    result = ''
    for d in data['RequestResult']['Accidents']:
        result += f'№ происшествия: {d["AccidentNumber"]}\nТип происшествия: {d["AccidentType"]}\nДата:' \
                  f' {d["AccidentDateTime"]}\nМесто происшествия: {d["AccidentPlace"]}\nСостояние ТС: ' \
                  f'{d["VehicleDamageState"]}\nКол-во участников ДТП: {d["VehicleAmount"]}\nПорядковый номер ТС в ДТП: ' \
                  f'{d["VehicleSort"]}\nРегион: {d["RegionName"]}\nМарка ТС: {d["VehicleMark"]}\nМодель ТС: ' \
                  f'{d["VehicleModel"]}\nГод выпуска ТС: {d["VehicleYear"]}\nОПФ собственника: {d["OwnerOkopf"]}\n\n'
    return result.strip()


def make_req(vincode, rucaptcha_key, action, max_attempts_available, proxies_sp, url_part):
    attempt = 0
    while True:
        attempt += 1
        proxy_use_all = proxies_sp[random.randint(0, len(proxies_sp) - 1)].replace('HTTP|', '').split('@')
        proxy_use = {'http': proxy_use_all[0]}
        print(f'---------------------------------------------\nПроверка VIN: {vincode},\nЭтап: {action},\n'
              f'Попытка {attempt} из {max_attempts_available},\nИспользуется proxy: {proxy_use}.\n')
        token = RuCaptcha("6Lc66nwUAAAAANZvAnT-OK4f4D_xkdzw5MLtAYFL",
                          f"https://xn--90adear.xn--p1ai/check/auto#{vincode}",
                          rucaptcha_key, action, proxy_use_all)
        print('Токен получен.')
        if token == 'Error':
            continue

        r = requests.post(f"https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/{url_part}",
                          data={"vin": vincode, "captchaWord": "", "checkType": "aiusdtp", "reCaptchaToken": token},
                          proxies=proxy_use)
        r = r.json()
        print(r)
        if not 'code' in r.keys() and 'status' in r.keys() and str(r['status']) != '201':
            if True:
                if action == 'check_auto_dtp':
                    return get_dtp_data(r)
                if action == 'check_auto':
                    return get_check_auto_limits(r)
                if action == 'check_auto_history':
                    return get_check_auto_history(r)
            #except Exception:
            #    print('error kek')
                pass
        if attempt == max_attempts_available:
            return 'Не удалось получить информацию. Этап: ' + action + '.'


def get_proxies():
    f = open('data_proxy.txt', 'r').read().split('\n')
    sp = []
    for proxy in f:
        proxy = proxy.split()
        if len(proxy) > 1:
            sp.append(proxy[2])
    return sp

def main(vin):
    RUCAPTCHA_KEY = '352fd27d3570790e2373223eb144ed09'
    site_dtp_action = 'check_auto_dtp'
    site_gibbd_history_action = 'check_auto_history'
    site_limit_action = 'check_auto'
    url_part_dtp = 'dtp'
    url_part_history = 'history'
    url_part_limits = 'restrict'
    max_attempts_available = 5
    proxies = get_proxies()
    result = ''
    result += make_req(vin, RUCAPTCHA_KEY, site_gibbd_history_action, max_attempts_available, proxies, url_part_history)
    result += make_req(vin, RUCAPTCHA_KEY, site_dtp_action, max_attempts_available, proxies, url_part_dtp)
    result += make_req(vin, RUCAPTCHA_KEY, site_limit_action, max_attempts_available, proxies, url_part_limits)

    print(result)


main('XTA219010D0114233')



