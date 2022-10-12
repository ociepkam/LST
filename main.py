import atexit
import csv
import random
import time
from os.path import join
import pandas as pd
from psychopy import visual, event, core

from code.load_data import load_config, load_images, prepare_block_stimulus
from code.screen_misc import get_screen_res
from code.show_info import part_info, show_info
from code.check_exit import check_exit

RESULTS = []
PART_ID = ""


@atexit.register
def save_beh_results():
    num = random.randint(100, 999)
    with open(join('results', '{}_beh_{}.csv'.format(PART_ID, num)), 'w', newline='') as beh_file:
        dict_writer = csv.DictWriter(beh_file, RESULTS[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(RESULTS)


def block(config, images, block_type,  win, fixation, clock, screen_res, answers):
    show_info(win, join('.', 'messages', f'instruction_{block_type}.txt'), text_color=config["text_color"],
              text_size=config["text_size"], screen_res=screen_res)

    n = -1
    for trial in images:
        key = None
        reaction_time = None
        acc = -1
        n += 1

        # fixation
        fixation.setAutoDraw(True)
        win.flip()
        time.sleep(config["fixation_time"])
        fixation.setAutoDraw(False)
        win.flip()

        # draw trial
        trial["stimulus"].setAutoDraw(True)
        win.callOnFlip(clock.reset)
        win.flip()
        while clock.getTime() < config["answer_time"]:
            key = event.getKeys(keyList=config["reaction_keys"])
            if key:
                reaction_time = clock.getTime()
                key = key[0]
                break
            check_exit()
            win.flip()

        trial["stimulus"].setAutoDraw(False)
        win.callOnFlip(clock.reset)
        win.callOnFlip(event.clearEvents)
        win.flip()

        # wait_time = config["wait_time"] + random.random() * config["wait_jitter"]
        # while clock.getTime() < wait_time:
        #     check_exit()
        #     win.flip()
        print(block_type, trial["image_ID"], "\n")
        print(answers.loc[(answers['item_type'] == block_type) &
                                         (answers['item_id'] == trial["image_ID"])]['answer'])
        correct_answer = str(answers.loc[(answers['item_type'] == block_type) &
                                         (answers['item_id'] == trial["image_ID"])]['answer'].iloc[0])
        if key:
            acc = 1 if key == correct_answer else 0
        trial_results = {"n": n, "block_type": block_type,
                         "rt": reaction_time, "acc": acc,
                         "stimulus": trial["image_name"],
                         "answer": key,
                         "correct_answer": correct_answer}
        RESULTS.append(trial_results)


def main():
    global PART_ID
    config = load_config()
    info, PART_ID = part_info()

    screen_res = dict(get_screen_res())
    win = visual.Window(list(screen_res.values()), fullscr=False, units='pix', screen=0, color=config["screen_color"])
    event.Mouse(visible=False)
    clock = core.Clock()
    fixation = visual.TextStim(win, color=config["fixation_color"], text=config["fixation_text"],
                               height=config["fixation_size"])

    answers = pd.read_csv(join("images", "answers.csv"))
    training_images, experimental_images = load_images(session=info["Session"], randomize=config["randomize_trails"])
    training_images = prepare_block_stimulus(training_images, win, config, folder="training")
    experimental_images = prepare_block_stimulus(experimental_images, win, config, folder="experiment")
    print(experimental_images)
    block(config=config, images=training_images, block_type="training", win=win, fixation=fixation,
          clock=clock, screen_res=screen_res, answers=answers)
    block(config=config, images=experimental_images, block_type="experiment", win=win, fixation=fixation,
          clock=clock, screen_res=screen_res, answers=answers)

    show_info(win, join('.', 'messages', f'end.txt'), text_color=config["text_color"],
              text_size=config["text_size"], screen_res=screen_res)


if __name__ == "__main__":
    main()
