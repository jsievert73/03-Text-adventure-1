import sys, logging, os, json

version = (3,7)
assert sys.version_info >= version, "This script requires at least Python {0}.{1}".format(version[0],version[1])

logging.basicConfig(format='[%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)




# Game loop functions
def render(room,maxHealth,Health):
    ''' Displays the current room, moves, and points '''

    print('\n\nMax Health: {mH}, CurrentHealth: {cH}'.format(mH=maxHealth, cH=Health))
    print('\n\nYou are in the {name}'.format(name=room['name']))
    print(room['desc'])


def getInput(verbs):
    ''' Asks the user for input and normalizes the inputted value. Returns a list of commands '''

    response = input('\nWhat would you like to do? ').strip().upper().split()
    if (len(response)):
        #assume the first word is the verb
        response[0] = normalizeVerb(response[0],verbs)
    return response


def update(response,room,current,inventory,game):
    ''' Process the input and update the state of the world '''
    s = list(response)[0]  #We assume the verb is the first thing typed
    if s == "":
        print("\nSorry, I don't understand.")
        return current
    elif s == 'HELP':
        printVerbs(room)
        print("USE")
        return current
    elif s == 'INVENT':
        printInvent(inventory)
        return current
    elif s == 'TAKE' :
        noitem = True
        for e in room['exits']:
            if s == e['verb']:
                InventFill(inventory,room)
                noitem = False
                return current
        if noitem:
            print('There is nothing to take.')
            return current
    elif s == 'ATTACK' :
        for e in room['exits']:
            if s == e['verb']:
                return Battle(inventory,room,current,game)
    elif s == 'TRADE' :
        for e in room['exits']:
            if s == e['verb']:
                return Trade(inventory,room,current,game)
    elif s == 'PET' :
        for e in room['exits']:
            if s == e['verb']:
                return Pet(inventory,room,current,game)
    elif s == 'USE' :
        missinghealth = 10 - game['rooms']['CHARACTER']['health']
        for e in inventory:
            if e == "Blue Berries":
                print("You eat the Blue Berries. They're delicious.")
                inventory.remove("Blue Berries")
                return current
            if e == "Red Berries":
                game['rooms']['CHARACTER']['health'] = game['rooms']['CHARACTER']['health'] -1
                print("You eat the Red Berries. You don't feel so well afterward. (-1)")
                inventory.remove("Red Berries")
                return current
            if e == "Potion":
                if missinghealth >= 5:
                    game['rooms']['CHARACTER']['health'] = game['rooms']['CHARACTER']['health'] +5
                    print("You consume the Potion (+5)")
                    inventory.remove("Potion")
                    return current
            if e == "Leg of Lamb":
                if missinghealth >= 3:
                    game['rooms']['CHARACTER']['health'] = game['rooms']['CHARACTER']['health'] +3
                    print("You consume the Leg of Lamb (+3)")
                    inventory.remove("Leg of Lamb")
                    return current
            if e == "Purple Berries":
                if missinghealth >= 1:
                    game['rooms']['CHARACTER']['health'] = game['rooms']['CHARACTER']['health'] +1
                    print("You consume the Purple Berries (+1)")
                    inventory.remove("Purple Berries")
                    return current
            if e == "Bear Stew":
                if missinghealth >= 3:
                    game['rooms']['CHARACTER']['health'] = game['rooms']['CHARACTER']['health'] +3
                    print("You consume your Bear Stew (+3)")
                    inventory.remove("Bear Stew")
                    return current
            if e == "Red Potion":
                game['rooms']['CHARACTER']['health'] = game['rooms']['CHARACTER']['health'] +5
                print("You consume the Red Potion (+9)")
                inventory.remove("Red Potion")
                return current
        print("You have nothing to consume, or it wouldn't heal you for the full value at this point.")
        return current
    else:
        for e in room['exits']:
            if s == e['verb'] and e['target'] != 'NoExit':
                print(e['condition'])
                return e['target']
    print("\nYou can't do that here!")
    return current


# Helper functions

def printVerbs(room):
    e = ", ".join(str(x['verb']) for x in room['exits'])
    print('\nYou can take the following actions: {directions}'.format(directions = e))
    print('INVENT')

def printInvent(invent):
    for e in invent:
        print(e)

def Battle(invent,room,current,game):
    playerstrength = 0
    for e in invent:
        if e == "Sword":
            if playerstrength < 1:
                playerstrength =1
        if e == "Sharpened Sword":
            if playerstrength < 2:
                playerstrength =2
        if e == "Dwarven Axe":
            if playerstrength < 3:
                playerstrength =3
        if e == "Sharpened Dwarven Axe":
            if playerstrength < 4:
                playerstrength = 4
        if e == "Dragon's Flame":
            playerstrength = 5
    for e in room['exits']:
            if "ATTACK" == e['verb'] and e['target'] != 'NoExit':
                rewriteroom = e['rewriteroom']
                rewritedirection = e['rewritedirection']
                rewrite = e['rewrite']
                print(e['condition'])
                game['rooms']['CHARACTER']['health'] = game['rooms']['CHARACTER']['health'] - (e['strength'])
                e['health'] = e['health'] - playerstrength
                if  e['health'] <= 0:
                    print(e['onkill'])
                    for d in game['rooms'][rewriteroom]['exits']:
                        if d['verb'] == rewritedirection:
                            d['target'] = rewrite;
                    if room == 'WIZARDFIGHT':
                        rewriteroom2 = e['rewriteroom2']
                        rewritedirection2 = e['rewritedirection2']
                        rewrite2 = e['rewrite2']
                        for c in game['rooms'][rewriteroom2]['exits']:
                            if c['verb'] == rewritedirection2:
                                c['target'] = rewrite2;
                    return e['target']
                else:
                    return current

def Pet(invent,room,current,game):
    for e in room['exits']:
            if "PET" == e['verb'] and e['target'] != 'NoExit':
                rewriteroom = e['rewriteroom']
                rewritedirection = e['rewritedirection']
                rewrite = e['rewrite']
                for d in game['rooms'][rewriteroom]['exits']:
                        if d['verb'] == rewritedirection:
                            d['target'] = rewrite;
                return e['target']

def Trade(invent,room,current,game):
    for e in room['exits']:
            if "TRADE" == e['verb'] and e['target'] != 'NoExit':
                rewriteroom = e['rewriteroom']
                rewritedirection = e['rewritedirection']
                rewrite = e['rewrite']
                for d in invent:
                    if d == e['item']:
                        invent.remove(d)
                        print(e['condition'])
                        for c in game['rooms'][rewriteroom]['exits']:
                            if c['verb'] == rewritedirection:
                                c['verb'] = rewrite;
                                return e['target']
                else:
                    print("You have nothing they want.")
                    return current

def InventFill(invent,room):
    for e in room['exits']:
            if "TAKE" == e['verb'] and e['target'] != 'NoExit':
                print(e['condition'])
                invent.append(e['item'])
                e['verb'] = "TAKEN"

def normalizeVerb(selection,verbs):
    for v in verbs:
        if selection == v['v']:
            return v['map']
    return ""

def end_game(winning,points,moves):
    if winning:
        print('\n\nYou have won! Congratulations')
        print('\nYou scored {points} points in {moves} moves! Nicely done!'.format(moves=moves, points=points))
    else:
        print('\n\nThanks for playing!')
        print('\nYou scored {points} points in {moves} moves. See you next time!'.format(moves=moves, points=points))





def main():

    # Game name, game file, starting location, winning location(s), losing location(s)
    games = [
        (   'My Game',          'game.json',    'THRONEROOM',    ['END'],    [])
        ,(  'Zork I',           'zork.json',    'WHOUS',    ['NIRVA'],  [])
        ,(  'A Nightmare',      'dream.json',    'START',   ['AWAKE'],  ['END'])
    ]

    inventory = []

    # Ask the player to choose a game
    game = {}
    while not game:
        print('\n\nWhich game would you like to play?\n')
        for i,g in enumerate(games):
            print("{i}. {name}".format(i=i+1, name=g[0]))
        try:
            choice = int(input("\nPlease select an option: "))
            game = games[choice-1]
        except:
            continue
            
    name,gameFile,current,win,lose = game





    with open(gameFile) as json_file:
        game = json.load(json_file)

    moves = 0
    points = 0
    health = 10
    maxHealth = 10
    inventory = []

    print("\n\n\n\nWelcome to {name}!\n\n".format(name=name))
    while True:
        if choice == 1:
            render(game['rooms'][current],game['rooms']['CHARACTER']['maxhealth'],game['rooms']['CHARACTER']['health'])
        else:
            render(game['rooms'][current],health,maxHealth)

        response = getInput(game['verbs'])

        if response[0] == 'QUIT':
            end_game(False,points,moves)
            break
        

        current = update(response,game['rooms'][current],current,inventory,game)
        if game['rooms']['CHARACTER']['health'] <= 0:
            current = "GAMEOVERBAD"
        moves = moves + 1

        if current in win:
            end_game(True,points,moves)
            break
        if current in lose:
            end_game(False,points,moves)
            break






if __name__ == '__main__':
	main()