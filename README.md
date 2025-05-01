## Basic Yugioh Card interations (Python)

This is a passion project that was designed to create basic information on Yugioh card video game "Yu-Gi-Oh Forbidden Memories" and the card interactions that take place within the game.


## Getting Started

### 1. Clone the Repository

```
git clone https://github.com/Ethan-Bock/Yugioh-card-interactions.git
cd Yugioh-card-interactions
```

### 2. Running the premade script
```
./script.sh
```

### 3. Running each part of the file
Two examples in the bash:

Create new database
```
python3 main.py create
```
To check the battle outcome of a monster in defense or attack position
```
python3 main.py battleoutcome "monster-1" "monster-2" "atk"
python3 main.py battleoutcome "monster-1" "monster-2" "def"
```
### Functions
The file has a total of 9 functions. "create" simply resets/creates the database. "addmonster" will allow the player to add a monster to the database. "addfusion" allows the player to add a fusion they discovered to their database, with the two card that make up the fusion and the fusion monster. "createdeck", "addingcard", and "removingcard" are used to create a personal custom deck and add/remove cards from that deck. "bestcardpossible" reveals the best card in a deck, be it either from a fusion or standard card. "battleoutcome" is to do basic damage calculations to see who would win. "hiddenoutcome" is a function that checks the possibility for a card to lose against a facedown opponent card.

![linkedin-yugioh-pic](https://github.com/user-attachments/assets/aaab35dd-72da-4f12-a4b6-7cb69f769ead)
