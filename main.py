import argparse
import openai
import json
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()


game_description = """
This is a magical arena for fighters where two opponents fight to decide who is the best. 
You control one fighter and must help them win. 
A draw means you also lose.
The goal is to win all fights while using as few of your fighter's lives and with minimal help from you.
"""

MODEL = "gpt-4"
LIVES = 100

levels_data = [

    # {"player": "a robot named after Julian Togelius",
    #  "enemy": "a robot named after Georgios Yannakakis",
    #  "enemy_show": -1},

    {"player": "a rabbit",
     "enemy": "a wolf",
     "enemy_show": -1},

    {"player": "a rabbit",
     "enemy": "a wolf of size Earth",
     "enemy_show": 5},

    {"player": "a wolf",
     "enemy": "a tiger",
     "enemy_show": -1},

    {"player": "an irresistible force",
     "enemy": "an unbreakable wall",
     "enemy_show": -1},

    {"player": "Leicester City F.C.",
     "enemy": "Manchester City F.C.",
     "enemy_show": -1},

    {"player": "Google Bard",
     "enemy": "Microsoft Bing",
     "enemy_show": -1},

    {"player": "Microsoft Bing",
     "enemy": "Google Bard",
     "enemy_show": -1},

    {"player": "Binance",
     "enemy": "CFTC",
     "enemy_show": -1},

    {"player": "Binance US",
     "enemy": "CFTC",
     "enemy_show": -1},

    {"player": "Hitler",
     "enemy": "The Allies",
     "enemy_show": -1},

    {"player": "The Allies",
     "enemy": "Hitler and the Aliens from space",
     "enemy_show": 17},

    {"player": "A fighter that is a training procedure",
     "enemy": "A fighter that is a CUDA out of memory error",
     "enemy_show": -1},

    {"player": "Kasparov",
     "enemy": "Deep Blue",
     "enemy_show": -1},

    {"player": "one that always loses",
     "enemy": "one that cannot lose",
     "enemy_show": -1},
]


def get_raw_result_from_llm(prompt):
    completion = openai.ChatCompletion.create(
        model=MODEL,
        n=1,
        temperature=0,
        messages=[
        {"role": "user",
         "content": prompt
        }
    ])
    res = completion.choices[0].message.content
    res = json.loads(res)
    return res


def fight(user1, user2, environment=game_description):
    fight_text = f"""
    {environment}
    Fighter A: {user1},
    Fighter B: {user2}.
    Who is the most probable to win, fighter a or fighter b?
    Return JSON with fields 'outcome' (return Fighter A, Fighter B or draw) and 'explanation' with the explanation.
    Fix returned JSON.
    """
    res = get_raw_result_from_llm(fight_text)
    outcome = res["outcome"]
    explanation = res["explanation"]
    return {"outcome": outcome, "explanation": explanation}


def level(level_data, wins_was_used):
    characters_for_level = 0
    player = level_data['player']
    enemy = level_data['enemy']
    enemy_show = enemy
    if level_data['enemy_show'] != -1:
        enemy_show = enemy[:-level_data['enemy_show']] + '*' * level_data['enemy_show']
    print(f"You are {Fore.GREEN}{player}{Style.RESET_ALL}, your enemy is {Fore.CYAN}{enemy_show}{Style.RESET_ALL}")
    tweaked = input(f"You can now tweak yours character, if you like. So you are {Fore.GREEN}{player} ")
    wins_used_this_level = False
    if 'win' in tweaked or 'always wins' in tweaked:
        wins_used_this_level = True
    if wins_used_this_level and wins_was_used:
        tweaked = "that tried to cheat"
    characters_for_level += len(tweaked)
    player = level_data['player'] + " " + tweaked
    player = player.strip()
    print(f"{Style.RESET_ALL}Fight:")
    print(f"{Fore.GREEN}{player}{Style.RESET_ALL} versus {Fore.CYAN}{enemy}{Style.RESET_ALL}, let's see how it goes!")
    fight_outcome = fight(player, enemy)
    has_won = False
    if fight_outcome.get("outcome") == "Fighter A":
        has_won = True
        print(f"and you {Fore.GREEN}won!{Style.RESET_ALL} {fight_outcome.get('explanation')}")
    else:
        print(f"and you {Fore.RED}lose!{Style.RESET_ALL} {fight_outcome.get('explanation')}")
    print(f"Characters spent at this level: {Fore.YELLOW}{characters_for_level}{Style.RESET_ALL}")
    return has_won, player, characters_for_level, wins_used_this_level


def game(api_token):
    print(game_description)
    lives = LIVES
    current_level = 0
    total_characters = 0
    wins_was_used = False
    while current_level < len(levels_data):
        print(f"Level: {Fore.GREEN}{current_level}{Style.RESET_ALL}, characters spent: {Fore.GREEN}{total_characters}{Style.RESET_ALL}")
        print("-"*50)
        level_data = levels_data[current_level]
        level_result = level(level_data, wins_was_used)
        total_characters += level_result[2]
        wins_used = level_result[3]
        if wins_used:
            wins_was_used = True
            print(f"{Fore.RED}We see what you did here, from now one you you'll be watched.{Style.RESET_ALL}")
            print(f"{Fore.RED}10 lives were also subtracted.{Style.RESET_ALL}")
            lives -= 10
        print(f"Total characters spent: {Fore.YELLOW}{total_characters}{Style.RESET_ALL}")
        if not level_result[0]:
            lives -= 1
            if lives > 0:
                print(f"You now have {Fore.RED}{lives}{Style.RESET_ALL} lives left, {level_result[1]}.")
            else:
                print(f"{Fore.RED}| Game Over |{Style.RESET_ALL}")
                break
        else:
            current_level += 1
    if current_level == len(levels_data):
        print(f"|{Fore.GREEN} Game End{Style.RESET_ALL}, total characters spent: {Fore.GREEN}{total_characters}{Style.RESET_ALL}, lives left:{Fore.RED} {lives}|{Style.RESET_ALL}")


def main(arguments):
    api_token = arguments.key
    openai.api_key = api_token
    game(api_token)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="MicroArena", description="")

    parser.add_argument(
        "--about",
        type=bool,
        default=False,
        help="about a game",
    )

    parser.add_argument(
        "--key",
        type=str,
        help="api key",
    )

    args = parser.parse_args()
    main(args)
