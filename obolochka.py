from gamecode import *

def get_materials():
    with open("AIres.txt", "r") as aires:
        return list(set(tuple(x.split("\n")) for x in aires.read().split("\n\n")))[:24]

materials = get_materials()
base = {} #player: data, score

choice = 1
while choice == 1:
    choice = int(input('начать игру?')) #у типа входное диалоговое окно
    if choice == 1:
        user = input('Введите имя: ') #недоработа с бд
        if user not in base:
            base[user] = ['win', 0]
            data = {'who': 'player', #вот это данные которыми обмениваются игра и оболчка, их не трогать!!!!
                    'player_hand': [],
                    'computer_hand': [],
                    'player_steps': [],
                    'plr_step': 0,
                    'comp_step': 'Взял карту',
                    'table': [],
                    'deck': []}
            data = gamestart(materials, data)
            print('first card:', data['table'][0].type, data['table'][0].text) #вывод первой карты на столе
            print('start')
        else:
            print('user data')
            print(base[user])
            if base[user][0] not in ('winner', 'loser'): #роверка на окончание прошлой игры (если пользователь закроет игру по середине, она сохранится
                data = base[user][0]
            else:
                data = {'who': input('Who started?'), #нициализация новой игры для сущ. пользователя
                        'player_hand': [],
                        'computer_hand': [],
                        'player_steps': [],
                        'plr_step': 0,
                        'comp_step': 'Взял карту',
                        'table': [],
                        'deck': []}
                data = gamestart(materials, data)
                print('first card:', data['table'][0].type, data['table'][0].text)
                print('start')
        while True:
            print('last card:', data['table'][-1].type, data['table'][-1].text) #вывод информации об игре. По сути тебе надо только last card, computer step, in hand остальное для отладки
            print('Computer step', data['comp_step'])
            print('Computer hand:', [(x.type, x.text) for x in data['computer_hand']])
            print('In deck', [(x.type, x.text) for x in data['deck']])
            print('In hand', [(x.type, x.text) for x in data['player_hand']])
            step = int(input('Step: ')) #ввод индекса карточки. По сути в оболчке с UI карточки по задумке нумеруются от 0 до  и нажатие на нужную возвращает номер, если игрок жмет на колоду (взять карту) должно вернуться -1
            data['plr_step'] = step
            data['who'] = 'player'
            data['comp_step'] = ''
            data = gameprocess(materials, data)
            base[user][0] = data
            if len(data) == 3: #нутри игрового кода, если игра оканчивается, дата заменяется на три данных для вывода о конце игры
                print('end')
                break
            else:
                print(data['plr_step']) #это вывод на экран хода игрока
        print(data) #вывод информации о пользователе и изменение счета data[0] - это имя победителя, data[1] кол-во верхых ходов/все ходы, data[2] - вывод ответов на карты, на которые игрок поставил не верную карту, это важно вывести
        print('mistakes', data[2])
        if data[0] == 'player':
            base[user][1] += data[1]
            base[user][0] = 'winner' #тут еще происходит изменение в базе данных о пользователе, изменяется его счет
        else:
            base[user][1] -= (1-data[1])
            base[user][0] = 'loser'
        print(data[1]) #не важный, просто вывод счета за игру
        print('results')
        print(base[user]) #в конце игры игрок видит все обновленные данные о себе в отдельном окне, после чего выходит обратно в диалоговое для начала игры