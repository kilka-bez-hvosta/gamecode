import random

class Card:
    def __init__(self, type, text):
        self.type = type
        self.text = text

class Player:
    def __init__(self):
        self.hand = []
        self.steps = []


class CardGame:
    def __init__(self, materials, first):
        self.materials = materials
        self.deck = []
        self.new_deck()
        self.player = Player()
        self.computer = Player()
        self.table = [self.deck.pop(0)]
        self.who = self.computer if first=="computer" else self.player

    def change(self):
        self.who = self.player if self.who == self.computer else self.computer

    def mix_deck(self):
        random.shuffle(self.deck)

    def new_deck(self):
        self.deck = ([Card("answer", x[1]) for x in self.materials] +
                     [Card("question", x[0]) for x in self.materials] +
                     [Card("blank_card", "") for _ in range(4)] +
                     [Card("change_hand", "") for _ in range(4)] +
                     [Card("gave_cards", "") for _ in range(4)] +
                     [Card("replace_cards", "") for _ in range(4)])
        self.mix_deck()

    def gave_card(self, whom, count=1):
        cards = []
        for _ in range(count):
            if self.deck:
                cards.append(self.deck.pop(-1))
            else:
                whom.hand.extend(cards)
                return "void", _
        whom.hand.extend(cards)
        return ''

    def check_step(self, card): #скинуть на стол можно карту, являющуюся вопрос или ответом к лежащей на столе
        if self.table[-1].type in ["blank_card",
                                   "change_hand",
                                   "gave_cards",
                                   "replace_cards"] or card.type in ["blank_card",
                                                                     "change_hand",
                                                                     "gave_cards",
                                                                     "replace_cards"]:
            return True
        elif self.table[-1].type == "answer":
            if (card.text, self.table[-1].text) in self.materials or card.type == "answer":
                return True
        elif self.table[-1].type == "question":
            if (self.table[-1].text, card.text) in self.materials or card.type == "question":
                return True
        return False

    def player_step(self, cardind, player1, player2):
        step = ''
        if cardind == -1: #если нет подходящей карты игрок должен будет вытягивать карты пока не сможет походить
            self.gave_card(player1)
            self.change()
            step = 'Взял карту'
        else:
            card = player1.hand.pop(cardind)#выложить карту на стол
            if self.check_step(card):
                player1.steps.append(("good"))
                if card.type == "change_hand": #карта меняет руки игроков
                    third = player2.hand.copy()
                    player2.hand = player1.hand.copy()
                    player1.hand = third
                elif card.type == "gave_cards": #карта дает 2 карты противнику
                    gave = self.gave_card(player2, 2)
                    if "void" in gave:
                        self.new_deck()
                        self.gave_card(player1, 2 - gave[2])

                elif card.type == "replace_cards": #карта скидывает имеющиеся карты игрока в колоду, перемешивает их и выдает игроку новую руку с тем же количеством карт
                    cnt = len(player1.hand)
                    self.deck += player1.hand.copy()
                    self.mix_deck()
                    player1.hand = []
                    gave = self.gave_card(player1, cnt)
                    if "void" in gave:
                        self.new_deck()
                        self.gave_card(player1, 2 - gave[2])
            else: #при неверной карте игрок получает две карты, одну вместо невернойодну штрафную
                self.player.steps.append(("bad", self.table[-2]))#записываем на какую карту игрок не смог походить подходящей картой, для вывода советов в конце
                take = self.gave_card(player1, 2)
                if "void" in take:
                    self.new_deck()
                    self.gave_card(player1, 2 - take[2])
            self.table = [self.table[-1], card]
            step = 'Выложил карту'
        self.change()
        return step

    def computer_step(self):
        output = ''
        flag_notmaded = True
        for cardind in range(len(self.computer.hand)):
            if self.check_step(self.computer.hand[cardind]):
                flag_notmaded = False
                card = self.computer.hand.pop(cardind)
                  # выложить карту на стол

                self.computer.steps.append(("good"))
                if card.type == "change_hand":  # карта меняет руки игроков
                    third = self.player.hand.copy()
                    self.player.hand = self.computer.hand.copy()
                    self.computer.hand = third
                elif card.type == "gave_cards":  # карта дает 2 карты противнику
                    self.gave_card(self.player, 2)
                elif card.type == "replace_cards":  # карта скидывает имеющиеся карты игрока в колоду, перемешивает их и выдает игроку новую руку с тем же количеством карт
                    cnt = len(self.computer.hand)
                    self.deck += self.computer.hand.copy()
                    self.mix_deck()
                    self.computer.hand = []
                    gave = self.gave_card(self.computer, cnt)
                    if "void" in gave:
                        self.new_deck()
                        self.gave_card(self.computer, 2 - gave[2])
                self.table = [self.table[-1], card]
                self.change()
                return 'Выложил карту'
        if flag_notmaded:
                self.gave_card(self.computer)
                return 'Взял карту'


def gamestop(player, computer):
    if len(player) == 0:
        return 'player'
    elif len(computer) == 0:
        return 'computer'
    return ''

#data: player_hand, computer_hand, player_steps, plr_step, comp_step, table, deck, who
def gameprocess(materials, data):
    game = CardGame(materials, data['who'])
    game.player.hand, game.player.steps, cardid = data['player_hand'], data['player_steps'], data['plr_step']
    game.computer.hand = data['computer_hand']
    game.table = data['table']
    game.deck = data['deck']
    gs = gamestop(game.player.hand, game.computer.hand)
    if gs:
        return gameend(materials, data, gs)
    data['plr_step'] = game.player_step(cardid, game.player, game.computer)
    data['comp_step'] = [game.computer_step()]
    data['player_hand'], data['player_steps'] = game.player.hand, game.player.steps
    data['computer_hand'] = game.computer.hand
    data['table'] = game.table
    data['deck'] = game.deck
    data['who'] = game.who
    gs = gamestop(game.player.hand, game.computer.hand)
    if gs:
        return gameend(materials, data, gs)
    return data




def gamestart(materials, data):
    game = CardGame(materials, data['who'])
    win = ''
    game.gave_card(game.player, 6)
    game.gave_card(game.computer, 6)
    data['comp_step'] = ''
    c = 0
    if data['who'] == 'computer':
        data['comp_step'] = [game.computer_step()]
        if game.who==game.computer:
            data['comp_step'] = [game.computer_step()]
            if game.who==game.computer:
                game.change()
    data['player_hand'], data['player_steps'] = game.player.hand, game.player.steps
    data['computer_hand'] = game.computer.hand
    data['comp_hand'] = game.computer.hand
    data['table'] = game.table
    data['deck'] = game.deck
    data['plr_step'] = ''
    data['who'] = game.who
    gs = gamestop(game.player.hand, game.computer.hand)
    if gs:
        return gameend(materials, data, gs)
    return data


def gameend(materials, data, winner):
    def right(member):
        for i in materials:
            if member.text in i:
                return i
        return member.text, 'нет подходящего'

    score = data['player_steps'].count('good')/len(data['player_steps'])
    advices = list(map(lambda x: right(x[1]), filter(lambda x: x != 'good', data['player_steps'])))
    return winner, score, advices