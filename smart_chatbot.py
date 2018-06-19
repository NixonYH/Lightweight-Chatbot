import sqlite3
from string import punctuation
import nltk
from nltk.tokenize import word_tokenize
import time


NAME = "Nyx_chatbot"
ENT = ["comment", "reply"]
ENT_TABLE = {"comment": "comments", "reply": "replies"}
ENT_ID = {"comment": "comment_id", "reply": "reply_id"}

BLACK_LIST = list("~@#$%&*`")
PUNCT = list(punctuation)

print("Connecting to {}'s database...".format(NAME))

conn = sqlite3.connect('{}.db'.format(NAME))
c = conn.cursor()

def create_table():
    table_to_create = ["CREATE TABLE interactions(comment_id INT NOT NULL, reply_id INT NOT NULL, occurrence INT NOT NULL DEFAULT 1, weight REAL NOT NULL DEFAULT 100)",
                "CREATE TABLE comments(comment TEXT UNIQUE, words TEXT UNIQUE)",
                "CREATE TABLE replies(reply TEXT UNIQUE, words TEXT UNIQUE)",
                "CREATE TABLE topic(user_comment TEXT UNIQUE, keyword TEXT UNIQUE)"]
    
    for i in range(len(table_to_create)):
        try:
            c.execute(table_to_create[i])
        except:
            pass


def get_id(entity_name, text):
    '''Retrieve an entity's unique ID from the database, given its associated text.
    If the row is not already present, it is inserted.
    The entity can either be a sentence or a word.
    '''
    all_words = list(text)
    words = list(filter(lambda a: a not in PUNCT, all_words))
    sent = "".join(words)
    words = ", ".join(word_tokenize(sent))

    table_name = ENT_TABLE[entity_name]
    column_name = entity_name

    c.execute("SELECT rowid FROM {} WHERE {} = ?".format(table_name, column_name), (text,))
    row = c.fetchone()

    if row:
        return row[0]
    else:
        print("Inserting value:", text, words)
        c.execute("INSERT INTO {}({}, words) VALUES (?, ?)".format(table_name, column_name), (text, words,))
        conn.commit()
        return c.lastrowid


def train(comment, reply):
    '''
    Saves the data into the database base on comment and reply
    '''
    comment_id = get_id("comment", comment)
    reply_id = get_id("reply", reply)

    c.execute("SELECT * FROM interactions")
    data = c.fetchall()

    not_occured = True

    for row in data:
        if comment_id == row[0] and reply_id == row[1]:
            not_occured = False
            own_occur = row[2] + 1

            c.execute("SELECT occurrence FROM interactions WHERE reply_id = ?", (reply_id,))

            all_occur = len(c.fetchall())
            weight = own_occur/(all_occur)*100
            c.execute("UPDATE interactions SET (weight, occurrence) = (?, ?) WHERE comment_id = ? AND reply_id = ?", (weight, own_occur, row[0], row[1],))
            break

        else:
            pass

    if not_occured:
        c.execute("INSERT INTO interactions(comment_id, reply_id) VALUES (?, ?)", (comment_id, reply_id,))

    conn.commit()


def get_reply(comment):
    '''
    Retrieve a reply base on the database.
    Before getting any replies, it will store the user_comment into the topic table and get the keywords.
    This will allow the chatbot to know more about what it is going to say!
    '''
    c.execute("INSERT INTO topic(user_comment)")

'''
DEFAULT CORPUS FORMAT:
L1045 +++$+++ u0 +++$+++ m0 +++$+++ BIANCA +++$+++ They do not!
'''

create_table()

train("Hi there!", "Hey, how are you?")

