from code.load_data import read_text_from_file
from psychopy import visual, gui, event


def part_info(test=False):
    if test:
        info = {'Part_id': '', 'Part_age': '20', 'Part_sex': 'MALE', 'Session': 1}
    else:
        info = {'Part_id': '', 'Part_age': '20', 'Part_sex': ['MALE', "FEMALE"], 'Session': [1, 2, 3]}
        dict_dlg = gui.DlgFromDict(dictionary=info, title='Stroop')
        if not dict_dlg.OK:
            exit(1)
    return info, f"{info['Part_id']}_{info['Part_sex']}_{info['Part_age']}_{info['Session']}"


def show_info(win, file_name, text_size, text_color, screen_res, insert=''):
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color=text_color, text=msg, height=text_size, wrapWidth=screen_res['width'])
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space'])
    if key == ['f7']:
        raise Exception('Experiment finished by user on info screen! F7 pressed.')
    win.flip()
