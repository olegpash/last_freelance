import time, ast
import pyautogui as auto
import pyperclip
import requests
from bs4 import BeautifulSoup



######## settings ########
start_now_position = (500, 1040)
elements_position = (1091, 113)
network_position = (1288, 113)
div_position = (1018, 426)
answer_position = (815, 300)
progress_position = (80, 1066)
show_position = (150, 1050)
next_position = (841, 1066)
filter_position = (1109, 174)
get_entry_position = (1161, 323)
enrty_position = (1363, 360)
clear_position = (1131, 144)
response_position = (1470, 300)
next_position = (944, 1066)
cancel_elements_position = (1501, 1070)
div_name = 'mediaCoverWrp'
network_filter = 'a.marathon'
######## settings ########


def get_hrefs():
    r = requests.get('https://driving-tests.org/')
    soup = BeautifulSoup(r.text, features='lxml')
    state_names = str(soup.findAll('div', {'id': 'blkStates'})).split('<li>')[1::]
    hrefs_for_states, states = [], []
    for state in state_names:
        fl, href_for_state = False, ''
        for i in state:
            if i == '"':
                fl = not fl
                if fl is False:
                    break
                continue
            if fl:
                href_for_state += i
        hrefs_for_states.append('https://driving-tests.org' + href_for_state)
        states.append(href_for_state.replace('/', ''))
    return hrefs_for_states, states
def parse_from_state(url):
    r = requests.get(url).text.split()
    fl1, fl2, fl3 = True, True, True
    first, second, third = '', '', ''
    for i in r:
        if 'marathon-practice-test' in i and fl1 is True:
            first = 'https://m.driving-tests.org' + i.replace('href="', '').replace('"', '')
            fl1 = not fl1
        if 'marathon-hard' in i and fl2 is True:
            if 'lnk' in i:
                continue
            second = 'https://m.driving-tests.org' + i.replace('href="', '').replace('"', '')
            fl2 = not fl2
        if 'marathon-hardest' in i and fl3 is True:
            if 'lnk' in i:
                continue
            third = 'https://m.driving-tests.org' + i.replace('href="', '').replace('"', '')
            fl3 = not fl3
    return [first, second, third]
def copy_to_buffer(phrase):
    pyperclip.copy(phrase)


def get_from_buffer():
    return pyperclip.paste()


def smart_click(cmd, *time_t):
    if len(time_t) != 0:
        time_t = 5  # error
    else:
        time_t = 0.5
    if cmd == '':
        pass
    else:
        auto.click(cmd)
    time.sleep(time_t)


def start_site():
    smart_click(elements_position)
    smart_click(cancel_elements_position)
    auto.hotkey('ctrl', 'f')
    smart_click('')
    copy_to_buffer(div_name)
    auto.hotkey('ctrl', 'v')
    smart_click('')
    auto.hotkey('enter')
    smart_click('')
    smart_click(div_position)
    auto.hotkey('delete')
    smart_click('')
    smart_click(cancel_elements_position)
    auto.rightClick(progress_position)
    smart_click('')
    smart_click(show_position)
    auto.hotkey('ctrl', 'c')
    time.sleep(1)
    buffer = get_from_buffer()
    smart_click(network_position)
    smart_click(get_entry_position)
    smart_click(response_position)
    smart_click(filter_position)
    auto.hotkey('ctrl', 'a')
    copy_to_buffer(network_filter)
    smart_click('')
    auto.hotkey('ctrl', 'v')
    smart_click('')
    return buffer


def check_answer(buffer, index):
    try:
    #if True:
        buffer = buffer.replace('"cbqInserted":true,', '').replace('"cbqInserted":false', '').split(',')
        anResult = buffer[0].replace('{"anResult":', '')
        uA = buffer[1].replace('"uA":', '').replace('"qA":', '')
        qA = buffer[2].replace('"qA":', '')
        if anResult == '1':
            buffer.insert(2, '3')
        description = ''
        for i in range(3, len(buffer)):
            if 'stats_a' in buffer[i]:
                idx = i
                break
            description += buffer[i]
        description = description.replace('"explanation":', '').replace('"', '')
        next_question = ''
        for i in range(idx + 1, len(buffer)):
            if '"images":' in buffer[i] or '"answers":' in buffer[i]:
                idx = i
                break
            next_question += buffer[i]
        next_question = next_question.replace('"question":{"text":"', '').replace('"', '')
        for i in range(len(next_question)):
            if next_question[i] == ']':
                next_question = next_question[i + 1::]
                break
        answers = ''
        fl = False
        for i in range(idx, len(buffer)):
            if '"answers":' in buffer[i]:
                fl = True
            if fl:
                answers += buffer[i]
            if ']' in buffer[i] and not '"images":' in buffer[i]:
                idx = i
                break
        answers = answers.replace('"answers":["', '').replace('"]', '').replace('""', '"').split('"')
        hint = ''
        for i in range(idx + 1, len(buffer)):
            if 'mposition' in buffer[i] or 'lwimage' in buffer[i] or 'updated' in buffer[i]:
                break
            else:
                hint += buffer[i]
        hint = hint.replace('"hint":', '').replace('"', '')
        if anResult == '0':
            answer = int(qA) + 1
        else:
            answer = int(uA) + 1
        return {'index': index, 'answer': answer, 'description': description, 'next_question': next_question, 'next_q_answers': answers,
                'next_q_hint': hint, 'buffer': buffer}

    except Exception:
        return {'index': index, 'answer': 'error', 'description': 'error', 'next_question': 'error', 'next_q_answers': 'error',
                'next_q_hint': 'error', 'buffer': buffer}


def write_log(data, name):
    with open(name + '.txt', 'a', encoding='utf-8') as log:
        log.write(str(data))
        log.write("\n")


def cycle(i, log_name):
    smart_click(clear_position)
    smart_click(answer_position)
    smart_click(get_entry_position)
    auto.tripleClick(enrty_position)
    smart_click('')
    auto.hotkey('ctrl', 'c')
    smart_click('')
    buffer = get_from_buffer()
    result = check_answer(buffer, i)
    write_log(str(result), log_name)
    auto.click(next_position)


def start_parsing_from_page(link, log_name):
    start_time = time.time()
    auto.hotkey('ctrl', 'w')
    time.sleep(1)
    auto.hotkey('ctrl', 't')
    time.sleep(1)
    copy_to_buffer(link)
    time.sleep(1)
    auto.hotkey('ctrl', 'v')
    time.sleep(1)
    auto.hotkey('enter')
    time.sleep(5)
    auto.hotkey('f12')
    time.sleep(1)
    auto.click(start_now_position)
    time.sleep(3)
    buffer = start_site()
    buffer = buffer.replace('<li class="ui-block-a"><button id="btnProgress" type="button" class="ui-link ui-btn ui-btn-b ui-state-disabled ui-btn-icon-left"><span class="ui-btn-inner"><span class="ui-icon ui-icon-grid">&nbsp;</span><span class="ui-btn-text">Progress</span><span id="qCounter">', '')
    buffer = buffer.replace('</span></span></button></li>', '').strip().split()
    count = int(buffer[2]) - int(buffer[0]) + 1
    for i in range(count):
        cycle(i, log_name)
    print(f'Page execution time: {time.time() - start_time} seconds.')


def start():
    with open('state_error.txt', 'a', encoding='utf-8') as log:
        log.write('\n')
    hrefs, states = get_hrefs()
    for href in range(len(hrefs)):
        try:
            links = parse_from_state(hrefs[href])
            with open(states[href] + '.txt', 'w', encoding='utf-8') as log:
                log.write("\n")
            for link in links:
                print(link, states[href])
                start_parsing_from_page(link, states[href])
        except Exception:
            with open('state_error.txt', 'a', encoding='utf-8') as log:
                log.write(states[href])
                log.write('\n')

time.sleep(5)
start()
