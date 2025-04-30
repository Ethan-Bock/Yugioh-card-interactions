#!/usr/bin/ python3

import click
import os
import sqlite3
import sys

DB_FILE = 'network.db'

def getdb(create=False):
    if os.path.exists(DB_FILE):
        if create:
            os.remove(DB_FILE)
    else:
        if not create:
            print('no database found')
            sys.exit(1)
    con = sqlite3.connect(DB_FILE)
    con.execute('PRAGMA foreign_keys = ON;')
    return con

@click.group()
def cli():
    pass

@click.command()
def create():
    with getdb(create=True) as con:

        # Monster Cards
        con.execute(
            '''CREATE TABLE cards (
                id             INTEGER PRIMARY KEY,
                name           TEXT NOT NULL,
                type           TEXT NOT NULL,
                lvl            INTEGER NOT NULL,
                atk            INTEGER NOT NULL,
                defe            INTEGER NOT NULL);''')
        con.execute('''CREATE UNIQUE INDEX cards_name ON cards (name)''')

        # Create Decks
        con.execute(
            '''CREATE TABLE decks (
                id          INTEGER PRIMARY KEY,
                deck_name    TEXT NOT NULL)''')
        con.execute('''CREATE UNIQUE INDEX created_decks ON decks (deck_name)''')

        # Add Cards to Deck
        con.execute(
            '''CREATE TABLE deckcards (
            id          INTEGER PRIMARY KEY,
            deck_id     INTEGER NOT NULL,
            card_id     INTEGER NOT NULL,
            FOREIGN KEY(deck_id) REFERENCES decks (id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(card_id) REFERENCES cards (id) ON DELETE CASCADE ON UPDATE CASCADE)''')

        # Fusions
        con.execute(
            '''CREATE TABLE fusions (
                card_one_id        INTEGER NOT NULL,
                card_two_id        INTEGER NOT NULL,
                fused_card_id      INTEGER NOT NULL,
                PRIMARY KEY(card_one_id, card_two_id),
                FOREIGN KEY(card_one_id) REFERENCES cards(id),
                FOREIGN KEY(card_two_id) REFERENCES cards(id),
                FOREIGN KEY(fused_card_id) REFERENCES cards(id))''')
        con.execute('''CREATE UNIQUE INDEX number_fusion ON fusions (card_one_id, card_two_id)''')
    print('database created')


@click.command()
@click.argument('name')
@click.argument('type')
@click.argument('lvl')
@click.argument('atk')
@click.argument('defe')
def addmonster(name, type, lvl, atk, defe):
    try:
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('''INSERT INTO cards (name, type, lvl, atk, defe) VALUES (?, ?, ?, ?, ?)''', (name, type, lvl, atk, defe))
            #print('Creating monster card', name)
            #id = cursor.lastrowid
            #print(f'inserted with id={id}.')
    except:
        print(f'Monster card {name} already exists.')


@click.command()
@click.argument('card_one')
@click.argument('card_two')
@click.argument('fused_card')
def addfusion(card_one, card_two, fused_card):
    try:
        cards = sorted([card_one, card_two])
        card_one = cards[0]
        card_two = cards[1]
        with getdb() as con:
            cursor = con.cursor()
            # Check if the fusion already exists
            cursor.execute('''SELECT COUNT(*) FROM fusions WHERE card_one_id = (SELECT id FROM cards WHERE name = ?) AND card_two_id = (SELECT id FROM cards WHERE name = ?)''', (card_one, card_two))
            result = cursor.fetchone()
            if result[0] > 0:
                print('Duplicate fusion exists for', card_one, 'and', card_two)
                return
            # If fusion does not exist, insert into the database
            cursor.execute('''INSERT INTO fusions (card_one_id, card_two_id, fused_card_id) VALUES ((SELECT id FROM cards WHERE name = ?), (SELECT id FROM cards WHERE name = ?), (SELECT id FROM cards WHERE name = ?))''', (card_one, card_two, fused_card))
            #print('Creating fusion for', fused_card, 'by fusing', card_one, 'and', card_two)
            #print(f'Fusion for {fused_card} created.')
    except Exception as e:
        print('Error:', e)



@click.command()
@click.argument('deck_name')
def createdeck(deck_name):
    try:
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('''INSERT INTO decks (deck_name) VALUES (?)''', (deck_name,))
            #print('Creating deck', deck_name)
    except:
        print(f'Deck {deck_name} already exists.')




@click.command()
@click.argument('deck_name')
@click.argument('card_name')
def addingcard(deck_name, card_name):
    try:
        with getdb() as con:
            cursor = con.cursor()
            # Check if the deck already contains 60 cards
            cursor.execute('''SELECT COUNT(*) FROM deckcards WHERE deck_id = (SELECT id FROM decks WHERE deck_name = ?)''', (deck_name,))
            card_count = cursor.fetchone()[0]
            if card_count >= 60:
                print('Cannot add more cards. Deck is already full.')
                return

            # Check if the deck already contains three cards of the same name
            cursor.execute('''SELECT COUNT(*) FROM deckcards WHERE deck_id = (SELECT id FROM decks WHERE deck_name = ?) AND card_id = (SELECT id FROM cards WHERE name = ?)''', (deck_name, card_name))
            same_card_count = cursor.fetchone()[0]
            if same_card_count >= 3:
                print(f'Cannot add more than three cards of the same name ({card_name}) to the deck.')
                return

            # If checks pass, insert the card into the deck
            cursor.execute('''INSERT INTO deckcards (deck_id, card_id) VALUES ((SELECT id FROM decks WHERE deck_name = ?), (SELECT id FROM cards WHERE name = ?))''', (deck_name, card_name))
            #print(f'Card {card_name} added to deck {deck_name}')
    except Exception as e:
        print('Error:', e)

@click.command()
@click.argument('deck_name')
@click.argument('card_id')
def removingcard(deck_name, card_id):
    try:
        with getdb() as con:
            cursor = con.cursor()

            # Check if the deck exists
            cursor.execute('''SELECT id FROM decks WHERE deck_name = ?''', (deck_name,))
            deck_result = cursor.fetchone()
            if not deck_result:
                print(f"Deck '{deck_name}' does not exist.")
                return

            # Check if the card exists in the deck
            cursor.execute('''SELECT id FROM deckcards WHERE deck_id = ? AND card_id = ?''', (deck_result[0], card_id))
            card_result = cursor.fetchone()
            if not card_result:
                print(f"Card with id '{card_id}' does not exist in deck '{deck_name}'.")
                return

            # Remove the card from the deck
            cursor.execute('''DELETE FROM deckcards WHERE deck_id = ? AND card_id = ?''', (deck_result[0], card_id))
            print(f"Card with id '{card_id}' removed from deck '{deck_name}'.")
    except Exception as e:
        print('Error:', e)



@click.command()
@click.argument('deck_name')
def bestcardpossible(deck_name):
    try:
        with getdb() as con:
            cursor = con.cursor()
            # Retrieve all cards in the specified deck
            cursor.execute('''SELECT c.name, c.atk, c.defe FROM deckcards dc JOIN cards c ON dc.card_id = c.id WHERE dc.deck_id = (SELECT id FROM decks WHERE deck_name = ?)''', (deck_name,))
            deck_cards = cursor.fetchall()
            best_fusion = None
            best_stats = 0
            used_cards = []  # Create used_cards list here
            
            # Iterate over each card in the deck
            for card in deck_cards:
                card_name, __, __ = card
                # Find possible fusions for the current card that involve cards in the deck
                cursor.execute('''SELECT f.fused_card_id, (c.atk + c.defe) AS total_stats, 
                  c.name AS fused_name, c.atk AS fused_atk, c.defe AS fused_defe,
                  c1.name AS card_one_name, c2.name AS card_two_name
                  FROM fusions f 
                  JOIN cards c ON f.fused_card_id = c.id 
                  JOIN cards c1 ON f.card_one_id = c1.id
                  JOIN cards c2 ON f.card_two_id = c2.id
                  WHERE (f.card_one_id = (SELECT id FROM cards WHERE name = ?) OR f.card_two_id = (SELECT id FROM cards WHERE name = ?))
                  AND (c1.name IN (SELECT c.name FROM deckcards dc JOIN cards c ON dc.card_id = c.id WHERE dc.deck_id = (SELECT id FROM decks WHERE deck_name = ?))
                  OR c2.name IN (SELECT c.name FROM deckcards dc JOIN cards c ON dc.card_id = c.id WHERE dc.deck_id = (SELECT id FROM decks WHERE deck_name = ?)))
                  AND f.fused_card_id NOT IN (SELECT card_id FROM deckcards WHERE deck_id = (SELECT id FROM decks WHERE deck_name = ?))''', 
                  (card_name, card_name, deck_name, deck_name, deck_name))
                possible_fusions = cursor.fetchall()
                
                # Iterate over possible fusions for the current card
                for fusion in possible_fusions:
                    fused_card_id, total_stats, fused_name, fused_atk, fused_defe, card_one_name, card_two_name = fusion
                    
                    # Check if both cards involved in the fusion are in the deck and not already used up
                    if (card_one_name in [c[0] for c in deck_cards] and card_two_name in [c[0] for c in deck_cards] and 
                        card_one_name not in used_cards and card_two_name not in used_cards):
                        
                        # Check if the current fusion has better stats
                        if total_stats > best_stats:
                            best_stats = total_stats
                            best_fusion = (card_one_name, card_two_name, fused_name, fused_atk, fused_defe)
                            used_cards.append(card_one_name)
                            used_cards.append(card_two_name)
                            
                            # Check for further fusions involving the newly created card
                            cursor.execute('''SELECT f.fused_card_id, (c.atk + c.defe) AS total_stats, 
                                c.name AS fused_name, c.atk AS fused_atk, c.defe AS fused_defe,
                                c1.name AS card_one_name, c2.name AS card_two_name
                                FROM fusions f 
                                JOIN cards c ON f.fused_card_id = c.id 
                                JOIN cards c1 ON f.card_one_id = c1.id
                                JOIN cards c2 ON f.card_two_id = c2.id
                                WHERE (f.card_one_id = ? OR f.card_two_id = ?)
                                AND f.fused_card_id NOT IN (SELECT card_id FROM deckcards WHERE deck_id = (SELECT id FROM decks WHERE deck_name = ?))''', 
                                (fused_card_id, fused_card_id, deck_name))
                            further_fusions = cursor.fetchall()
                            
                            # Iterate over further fusions involving the newly created card
                            for further_fusion in further_fusions:
                                further_fused_card_id, further_total_stats, further_fused_name, further_fused_atk, further_fused_defe, card_name, fused_card = further_fusion
                                
                                # Check if the current further fusion has better stats
                                if further_total_stats > best_stats:
                                    # Check if the card that combines with the fused_card is in the deck and not in used_cards
                                    if card_name in [c[0] for c in deck_cards] and further_fused_name not in used_cards:
                                        best_stats = further_total_stats
                                        best_fusion = (card_name, fused_card, further_fused_name, further_fused_atk, further_fused_defe)  # Use the original card name for the first card
                                        used_cards.append(further_fused_name)
                                    
            # Print the best fusion found
            if best_fusion:
                print(f"The best fusion for the deck '{deck_name}' is to fuse '{best_fusion[0]}' with '{best_fusion[1]}' to get '{best_fusion[2]}' with atk {best_fusion[3]} and defe {best_fusion[4]}.")
            else:
                print(f"No valid fusion found for the deck '{deck_name}'.")
    except Exception as e:
        print('Error:', e)


@click.command()
@click.argument('attacker_name')
@click.argument('reciever_name')
@click.argument('reciever_stance')
def battleoutcome(attacker_name, reciever_name, reciever_stance):
    try:
        with getdb() as con:
            cursor = con.cursor()
            # Fetch attacker's attack stat
            cursor.execute('''SELECT atk FROM cards WHERE name = ?''', (attacker_name,))
            attacker_atk = cursor.fetchone()[0]
            
            # Fetch receiver's attack and defense stats based on the stance
            if reciever_stance == 'def' or reciever_stance == 'defense':
                cursor.execute('''SELECT defe FROM cards WHERE name = ?''', (reciever_name,))
                receiver_stat = cursor.fetchone()[0]
                if attacker_atk > receiver_stat:
                    print(f"{attacker_name} sent {reciever_name} to the graveyard!")
                elif attacker_atk < receiver_stat:
                    print(f"{reciever_name} had stronger defense and sent {reciever_name} to the graveyard!")
                else:
                    print("It's a tie! Neither card is destroyed!")

            elif reciever_stance == 'atk' or reciever_stance == 'attack':
                cursor.execute('''SELECT atk FROM cards WHERE name = ?''', (reciever_name,))
                receiver_stat = cursor.fetchone()[0]
                if attacker_atk > receiver_stat:
                    print(f"{attacker_name} sent {reciever_name} to the graveyard, and opposing player recieves {attacker_atk - receiver_stat} damage points!")
                elif attacker_atk < receiver_stat:
                    print(f"{reciever_name} was stronger and sent {reciever_name} to the graveyard, and attacking player recieves {receiver_stat - attacker_atk} damage points!")
                else:
                    print(f"{attacker_name} and {reciever_name} are equal in strength and both are sent to the graveyard!")
            else:
                print("Invalid receiver stance. Please provide 'def' or 'atk'.")
                return

    except Exception as e:
        print('Error:', e)


@click.command()
@click.argument('card_name')
def hiddenoutcome(card_name):
    try:
        with getdb() as con:
            cursor = con.cursor()
            cursor.execute('''
                SELECT 
                    (SELECT COUNT(*) FROM cards WHERE defe < (SELECT atk FROM cards WHERE name = ?)) * 1.0 / 
                        (SELECT COUNT(DISTINCT name) FROM cards WHERE name != ?) AS probability,
                    GROUP_CONCAT(name) AS higher_attack_monsters
                FROM cards
                WHERE defe > (SELECT atk FROM cards WHERE name = ?) AND name != ?''', (card_name, card_name, card_name, card_name))
            result = cursor.fetchone()
            probability = result[0]
            higher_attack_monsters = result[1]
            
            print(f"The probability that {card_name} will have a higher attack than other monsters' defense is {probability}")
            if higher_attack_monsters:
                print(f"Monsters with higher defense than {card_name}'s attack:")
                for monster_name in higher_attack_monsters.split(','):
                    print(monster_name)
            else:
                print(f"There are no monsters with higher defense than {card_name}'s attack.")
    except Exception as e:
        print('Error:', e)


cli.add_command(create)
cli.add_command(addmonster)
cli.add_command(addfusion)
cli.add_command(createdeck)
cli.add_command(addingcard)
cli.add_command(removingcard)
cli.add_command(bestcardpossible)
cli.add_command(battleoutcome)
cli.add_command(hiddenoutcome)
cli()
