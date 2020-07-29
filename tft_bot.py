import pyautogui
import time
import ctypes
import sys
import argparse
import pywinauto

from pywinauto                import application
from pywinauto.findwindows    import find_window
from pywinauto.win32functions import SetFocus
from pywinauto.win32functions import ShowWindow
from pywinauto.keyboard import send_keys, KeySequenceError

# TODO: turn this into an enum
IMAGES = {
    "debug.gold" : "data/debug_gold.png",

    "client.find_match" : 'data/client_find_match.png',
    "client.accept" : 'data/client_accept.png',
    "client.ok" : 'data/client_ok.png',
    "client.play_again" : 'data/client_play_again.png',

    "champs.malphite" : 'data/champs_malphite.png',
    "champs.yasuo" : 'data/champs_yasuo.png',
    "champs.yi" : 'data/champs_yi.png',
    "champs.zed" : 'data/champs_zed.png',
    "champs.ziggs" : 'data/champs_ziggs.png',

    "game.reroll" : 'data/game_reroll.png',
    "game.gold.0" : 'data/game_gold_0.png',
    "game.gold.1" : 'data/game_gold_1.png',

    "game.item.gold" : 'data/game_item_gold.png',
    "game.item.blue" : 'data/game_item_blue.png',
    "game.item.gray" : 'data/game_item_gray.png',

    "game.time_approx.0" : 'data/game_time_approx_0.png',
    "game.stage.1-1" : 'data/game_stage_1_1.png',
    "game.stage.1-2" : 'data/game_stage_1_2.png',
    "game.stage.1-3" : 'data/game_stage_1_3.png',
    "game.stage.1-4" : 'data/game_stage_1_4.png',
    "game.stage.2-1" : 'data/game_stage_2_1.png',
    "game.stage.2-2" : 'data/game_stage_2_2.png',
    "game.stage.2-3" : 'data/game_stage_2_3.png',
    "game.stage.2-4" : 'data/game_stage_2_4.png',
    "game.stage.2-5" : 'data/game_stage_2_5.png',
    "game.stage.2-6" : 'data/game_stage_2_6.png',
    "game.stage.2-7" : 'data/game_stage_2_7.png',
    "game.stage.3-1" : 'data/game_stage_3_1.png',
    "game.stage.3-2" : 'data/game_stage_3_2.png',
    "game.stage.3-3" : 'data/game_stage_3_3.png',
    "game.stage.3+" : 'data/game_stage_3+.png',

    "game.reference_icon" : 'data/game_reference_icon.png',
    "game.settings" : 'data/game_settings.png',
    "game.surrender" : 'data/game_surrender.png',
    "game.surrender_confirmation" : 'data/game_surrender_confirmation.png',
    "game.continue" : 'data/game_continue.png',
}

WINDOWS = {
    "client" : "League of Legends",
    "game" : "League of Legends (TM) Client",
}

def add_coordinates(coord1, coord2):
    return (coord1[0] + coord2[0], coord1[1] + coord2[1])

def find_image(name, log=True, confidence=0.9):
    start = time.time()
    image = pyautogui.locateOnScreen(IMAGES[name], confidence=confidence)
    elapsed = time.time() - start
    if log:
        if image is not None:
            print(f"<{name}> Found: {image}")
        else:
            print(f"<{name}> Timedout")
        print(f"  {elapsed} seconds")
    return image

def click(name, image, use_press=False):
    print(f"Clicking on {name}")
    print(image)
    if use_press:
        pywinauto.mouse.press(coords=(image.left, image.top))
        time.sleep(0.1)
        pywinauto.mouse.release()
    else:
        pywinauto.mouse.click(coords=(image.left, image.top))

def move_unit(desc, location, reference_coord=(0, 0)):
    new_location = add_coordinates(reference_coord, location)
    pywinauto.mouse.click(button='right', coords=(new_location[0], new_location[1]))

def wait_for_image(name, timeout=0):
    result = wait_for_images([name], timeout)
    if result is not None:
        return result[1]
    return None

def wait_for_images(names, timeout=0):
    start = time.time()
    print(f"<{names}>: Waiting")
    while True:
        print(".", end="", flush=True)
        elapsed = time.time() - start
        if timeout != 0 and elapsed > timeout:
            return None
        for name in names:
            image = find_image(name, log=False)
            if image is not None:
                print("")
                print(f"  {elapsed} seconds")
                return (name, image)
        time.sleep(0.2)

def get_window(name):
    windows = pywinauto.findwindows.find_windows(title=WINDOWS[name])
    if len(windows) == 0:
        print(f"ERROR: Couldn't find window {name}")
        return None
    app = application.Application()
    app.connect(handle=windows[0])
    return app

##################
# League
##################

STAGES = {
    (1, 1) : "game.stage.1-1",
    (1, 2) : "game.stage.1-2",
    (1, 3) : "game.stage.1-3",
    (1, 4) : "game.stage.1-4",
    (2, 1) : "game.stage.2-1",
    (2, 2) : "game.stage.2-2",
    (2, 3) : "game.stage.2-3",
    (2, 4) : "game.stage.2-4",
    (2, 5) : "game.stage.2-5",
    (2, 6) : "game.stage.2-6",
    (2, 7) : "game.stage.2-7",
    (3, 1) : "game.stage.3-1",
    (3, 2) : "game.stage.3-2",
    (3, 3) : "game.stage.3-3",
    (3, 10) : "game.stage.3+",
}
SORTED_STAGES = sorted(STAGES)

def get_current_stage(previous_stage):
    stage_to_check = (0, 0)
    for stage in SORTED_STAGES:
        if previous_stage < stage:
            stage_to_check = stage
            break

    if stage_to_check == (0, 0):
        return (0, 0)

    if find_image(STAGES[stage_to_check], log=False) is not None:
        return stage_to_check

    return previous_stage

CAROUSEL_COORDS = [
    (1000, 600),
    (1130, 550),
    (1050, 380),
    (850, 380),
    (850, 600),
]

def pick_carousel_initial(reference_coord):
    print("play_tft/picking_carousel")
    if reference_coord is None:
        return
    
    time.sleep(4)
    move_unit(None, (800, 700), reference_coord)
    wait_for_image("game.time_approx.0")
    print("Countdown from 3")
    time.sleep(3)
    print("Countdown at 0")

    move_carousel(reference_coord)

def move_carousel(reference_coord):
    move_unit(None, CAROUSEL_COORDS[0], reference_coord)
    time.sleep(2)
    move_unit(None, CAROUSEL_COORDS[1], reference_coord)
    time.sleep(3)
    move_unit(None, CAROUSEL_COORDS[2], reference_coord)
    time.sleep(2)
    move_unit(None, CAROUSEL_COORDS[3], reference_coord)
    time.sleep(3)
    move_unit(None, CAROUSEL_COORDS[4], reference_coord)

ITEM_COORDS = [
    (1000, 600),
    (1130, 550),
    (1050, 380),
    (850, 380),
    (850, 600),
]

def has_0_gold():
    return find_image("game.gold.0", log=False)

def has_1_gold():
    return find_image("game.gold.1", log=False)

def reroll():
    rerolling = has_0_gold() or has_1_gold()
    if rerolling:
        do_reroll()
    return rerolling

def do_reroll():
    send_keys("{d down}{d up}")

def find_item():
    item = find_image("game.item.blue", confidence=0.7, log=False)
    if item is not None:
        return item
    item = find_image("game.item.gold", confidence=0.7, log=False)
    if item is not None:
        return item
    item = find_image("game.item.gray", confidence=0.7, log=False)
    if item is not None:
        return item

def walk_to_item():
    item = find_item()
    if item is not None:
        print("walk_to_item/found_items")
        move_unit("game.item", (item.left, item.top))
        time.sleep(0.2)
        move_unit("game.item", (item.left, item.top))
        time.sleep(1)
        move_unit("game.item", (item.left, item.top))

def surrender():
    print("play_tft/surrender/start")
    send_keys("{VK_ESCAPE}")

    time.sleep(0.5)

    surrender_button = wait_for_image("game.surrender")
    pywinauto.mouse.move(coords=(surrender_button.left, surrender_button.top))
    time.sleep(0.1)
    # TODO: Can we use the click API? (next line)
    pywinauto.mouse.click(coords=(surrender_button.left, surrender_button.top))

    time.sleep(0.3)

    surrender_confirmation = wait_for_image("game.surrender_confirmation")
    # TODO: Can we use the click API? (next 3 lines)
    pywinauto.mouse.press(coords=(surrender_confirmation.left, surrender_confirmation.top))
    time.sleep(1)
    pywinauto.mouse.release(coords=(surrender_confirmation.left, surrender_confirmation.top))

    time.sleep(3)

    print("play_tft/surrender/finish")

CHAMPS = [
    "champs.malphite",
    "champs.yasuo",
    "champs.yi",
    "champs.zed",
    "champs.ziggs",
]

def pick_champs(reference_coord):
    for champ in CHAMPS:
        champ_button = find_image(champ, log=False)
        if champ_button is not None:
            # TODO: can we use the click API? (next 8 lines)
            pywinauto.mouse.press(coords=(champ_button.left, champ_button.top))
            pywinauto.mouse.release(coords=(champ_button.left, champ_button.top))
            time.sleep(0.1)
            pywinauto.mouse.press(coords=(champ_button.left, champ_button.top))
            pywinauto.mouse.release(coords=(champ_button.left, champ_button.top))
            time.sleep(0.1)
            pywinauto.mouse.press(coords=(champ_button.left, champ_button.top))
            pywinauto.mouse.release(coords=(champ_button.left, champ_button.top))

def get_reference_coordinate():
    reference_icon = find_image("game.reference_icon", log=False)
    if reference_icon == None:
        return None
    return (reference_icon.left - 1885, reference_icon.top - 110)

def play_tft(override_stage=None):
    print(f"play_tft/start")
    previous_stage = (-1, 0)
    reference_coord = None
    iteration_count = 0
    while True:
        stage = get_current_stage(previous_stage)
        if override_stage != None:
            stage = override_stage
        if stage != previous_stage:
            print(f"play_tft/{stage[0]}-{stage[1]}, iterations={iteration_count}")
            if reference_coord == None:
                reference_coord = get_reference_coordinate()
                print(f"play_tft/reference_coord={reference_coord}")

            iteration_count = 0
            if stage == (1, 1):
                pick_carousel_initial(reference_coord)
            elif stage == (2, 4):
                move_carousel(reference_coord)
                move_carousel(reference_coord)
            elif stage[0] == 3 and stage != (3, 1):
                surrender()
                print("play_tft/done")
                return
            else:
                if previous_stage != (-1, 0) and stage == (0, 0):
                    return

        if stage != (0, 0) and stage != (2, 4):
            gold_0 = has_0_gold()
            gold_1 = has_1_gold()
            if not gold_0:
                pick_champs(reference_coord)
                # move the cursor away so it doesn't block any text
                pywinauto.mouse.move(coords=reference_coord)
            if not gold_0 and not gold_1:
                do_reroll()
            walk_to_item()

        # TODO: if somehow we lost the game, the continue button should show
        # we should exit find_image(game.continue)
        
        # only sleep if no time has passed
        time.sleep(0.2)
        previous_stage = stage
        iteration_count += 1

def focus_game_window():
    game_app = get_window("game")
    game_app.window().set_focus()

def focus_client_window():
    client_app = get_window("client")
    client_app.window().set_focus()

def run_loop_from_client(limit=0):
    focus_client_window()

    iteration_count = 0
    while True:
        find_match_button = wait_for_image("client.find_match", timeout=0)
        click("client.find_match", find_match_button)

        while True:
            name, image = wait_for_images(["game.stage.1-1", "client.accept"], timeout=0)
            if name is None or image is None:
                print("Error: something went wrong waiting for the game to start")
                return
            if name == "game.stage.1-1":
                break
            else: # "client.accept"
                click(name, image)

        play_tft()

        # focus_client_window()

        find_ok_button = wait_for_image("client.ok", timeout=3)
        if find_ok_button is not None:
            click("client.ok", find_ok_button)

        play_again_button = wait_for_image("client.play_again", timeout=0)
        click("client.play_again", play_again_button)

        iteration_count += 1
        if iteration_count >= limit and limit != 0:
            return

def run_test():    
    # focus_game_window()
    # reference_coord = get_reference_coordinate()

    # test_buy_champs()
    # walk_to_item()
    print(wait_for_images(["client.find_match", "client.find_match"], timeout=0))

def main():
    parser = argparse.ArgumentParser(description='play tft')

    parser.add_argument('--round', type=str,
                        help='The override round to start')
    parser.add_argument('--test', action='store_true',
                        help='indicates if we should run test')
    parser.add_argument('--surrender', action='store_true',
                        help='')
    parser.add_argument('--pick-champ', action='store_true',
                        help='')
    parser.add_argument('--reroll', action='store_true',
                        help='')
    parser.add_argument('--limit', type=int,
                        help='')
    args = parser.parse_args()
    print(args)

    if args.test:
        run_test()
    elif args.surrender:
        focus_game_window()
        surrender()
    elif args.pick_champ:
        focus_game_window()
        reference_coord = get_reference_coordinate()
        pick_champs(reference_coord)
    elif args.reroll:
        reroll()
    elif args.round is not None:
        stage_raw = args.round.split(".")
        stage = (int(stage_raw[0]), int(stage_raw[1]))
    
        focus_game_window()
        play_tft(stage)

        focus_client_window()

        find_ok_button = wait_for_image("client.ok", timeout=3)
        if find_ok_button is not None:
            click("client.ok", find_ok_button)

        play_again_button = wait_for_image("client.play_again", timeout=0)
        click("client.play_again", play_again_button)
    else:
        run_loop_from_client(limit=args.limit)

if __name__ == "__main__":
    main()
