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


def draw_stim_list(stim_list, flag):
    for elem in stim_list:
        elem.setAutoDraw(flag)


def block(config, images, block_type, win, fixation, clock, screen_res, answers, answers_buttons, mouse):
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

        trial["stimulus"].setAutoDraw(True)
        win.callOnFlip(clock.reset)

        # draw trial for answers_type == keyboard
        if config["answers_type"] == "keyboard":
            win.flip()
            while clock.getTime() < config["answer_time"]:
                key = event.getKeys(keyList=config["reaction_keys"])
                if key:
                    reaction_time = clock.getTime()
                    key = key[0]
                    break
                check_exit()
                win.flip()

        # draw trial for answer_type == mouse
        else:
            draw_stim_list(answers_buttons.values(), True)
            win.flip()
            while clock.getTime() < config["answer_time"] and key is None:
                for k, ans_button in answers_buttons.items():
                    if mouse.isPressedIn(ans_button):
                        reaction_time = clock.getTime()
                        key = str(k)
                        break
                    elif ans_button.contains(mouse):
                        ans_button.borderWidth = config["answer_box_width"]
                    else:
                        ans_button.borderWidth = 0
                check_exit()
                win.flip()
            draw_stim_list(answers_buttons.values(), False)

        # cleaning
        trial["stimulus"].setAutoDraw(False)
        win.callOnFlip(clock.reset)
        win.callOnFlip(event.clearEvents)
        win.flip()

        wait_time = config["wait_time"] + random.random() * config["wait_jitter"]
        while clock.getTime() < wait_time:
            check_exit()
            win.flip()

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
    info, PART_ID = part_info(test=False)

    screen_res = dict(get_screen_res())
    win = visual.Window(list(screen_res.values()), fullscr=False, units='pix', screen=0, color=config["screen_color"])

    if config["answers_type"] == "keyboard":
        mouse = event.Mouse(visible=False)
    elif config["answers_type"] == "mouse":
        mouse = event.Mouse(visible=True)
    else:
        raise Exception("Wrong config answers_type. Choose answers_type == (keyboard or mouse)")

    clock = core.Clock()
    fixation = visual.TextStim(win, color=config["fixation_color"], text=config["fixation_text"],
                               height=config["fixation_size"])
    answers_buttons = {i: visual.ButtonStim(win, color=config["answer_color"], text=config["answer_symbols"][i],
                                            letterHeight=config["answer_size"], pos=config["answer_pos"][i],
                                            borderColor=config["answer_box_color"], borderWidth=0,
                                            size=config["answer_box_size"], fillColor=config["answer_fill_color"])
                       for i in config["answer_symbols"]}

    # load data and prepare trials
    answers = pd.read_csv(join("images", "answers.csv"))
    training_images, experimental_images = load_images(session=info["Session"], randomize=config["randomize_trails"])
    training_images = prepare_block_stimulus(training_images, win, config, folder="training")
    experimental_images = prepare_block_stimulus(experimental_images, win, config, folder="experiment")

    # run blocks
    block(config=config, images=training_images, block_type="training", win=win, fixation=fixation,
          clock=clock, screen_res=screen_res, answers=answers, answers_buttons=answers_buttons, mouse=mouse)
    block(config=config, images=experimental_images, block_type="experiment", win=win, fixation=fixation,
          clock=clock, screen_res=screen_res, answers=answers, answers_buttons=answers_buttons, mouse=mouse)

    # end info
    show_info(win, join('.', 'messages', f'end.txt'), text_color=config["text_color"],
              text_size=config["text_size"], screen_res=screen_res)


if __name__ == "__main__":
    main()
