import atexit
import csv
import random
from os.path import join
from psychopy import visual, event, core

from code.load_data import load_config
from code.screen_misc import get_screen_res
from code.show_info import part_info, show_info

RESULTS = []
PART_ID = ""


@atexit.register
def save_beh_results():
    num = random.randint(100, 999)
    with open(join('results', '{}_beh_{}.csv'.format(PART_ID, num)), 'w') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)


def main():
    global PART_ID
    config = load_config()
    info, PART_ID = part_info()

    screen_res = dict(get_screen_res())
    win = visual.Window(list(screen_res.values()), fullscr=True, units='pix', screen=0, color=config["screen_color"])
    event.Mouse(visible=False)
    clock = core.Clock()
    fixation = visual.TextStim(win, color=config["fixation_color"], text=config["fixation_text"],
                               height=config["fixation_size"])


if __name__ == "__main__":
    main()
