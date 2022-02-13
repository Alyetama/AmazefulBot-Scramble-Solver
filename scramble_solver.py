import os
import re
import socket
import sys
import time
from collections import Counter

from dotenv import load_dotenv
from loguru import logger


def words():
    with open('/usr/share/dict/words') as f:
        dictionary = f.read()
    return [x.lower() for x in dictionary.split('\n')]


def return_anagrams(letters: str) -> list:
    global dictionary
    assert isinstance(letters, str)

    letters = letters.lower()
    letters_count = Counter(letters)
    anagrams = set()

    for word in dictionary:
        if not set(word) - set(letters):
            check_word = set()
            for k, v in Counter(word).items():
                if v == letters_count[k]:
                    check_word.add(k)
            if check_word == set(word) and len(word) == len(letters):
                anagrams.add(word)

    return list(anagrams)


def chat(sock, msg):
    sock.send("PRIVMSG {} :{}\r\n".format(CHAN, msg).encode("utf-8"))


def get_response():
    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    response = s.recv(1024).decode("utf-8")
    if response == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
    else:
        username = re.search(r"\w+", response).group(0)
        message = CHAT_MSG.sub("", response)
        return username, message


def main():
    while True:
        try:
            username, message = get_response()
            if not username or not message:
                continue
        except (ConnectionResetError, TypeError):
            continue

        if username == 'amazefulbot' and message.startswith(
                '[Scramble]') and 'FeelsGoodMan' not in message and 'Hint' not in message:
            logger.info(message)
            word = message.split(': ')[1].split(' ')[0]
            logger.info(f'Word: {word}')
            test_anagrams = return_anagrams(word)
            logger.info(test_anagrams)

            for n, w in enumerate(test_anagrams):
                time.sleep(1)
                chat(s, w)
                logger.info(f'attempt {n + 1}/{len(test_anagrams)}: {w}')
                try:
                    username, message = get_response()
                except ConnectionResetError:
                    continue
                if username == 'amazefulbot' and message.startswith(
                        '[Scramble]') and 'FeelsGoodMan' in message:
                    break


if __name__ == '__main__':
    logger.add('logs.log')
    load_dotenv()
    dictionary = words()
    HOST = "irc.chat.twitch.tv"
    PORT = 6667
    NICK = os.environ['NICK']
    PASS = os.environ['PASS']
    CHAN = '#' + os.environ['CHAN']
    s = socket.socket()
    s.connect((HOST, PORT))
    s.send("PASS {}\r\n".format(PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(NICK).encode("utf-8"))
    s.send("JOIN {}\r\n".format(CHAN).encode("utf-8"))
    try:
        main()
    except KeyboardInterrupt:
        s.close()
        sys.exit(0)
