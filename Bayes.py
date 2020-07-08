from itertools import islice

import os
import glob
import os
import glob
import smtplib
import time
import imaplib
import re
import email
import re
from math import log


def przegladanie_plikow(directory):
    lista_słów = []
    częstotliwość_słów = {}
    n = 0
    ilość_maili = 0
    długości_maili = 0
    ilosc_plików = len([name for name in os.listdir(directory)])

# WERSJA 1, pamietaj o tabie kurde
#    while n <= ilosc_plików:
#        n += 1
#        filenames_dir = glob.glob(os.path.join(directory + "/" + str(n).zfill(2), '*.txt'))
#        for filename in filenames_dir:


#WERSJA 2
    for filenames in os.listdir(directory):
        n += 1
        #print(dir)
        filename = directory + '/' + filenames
        #print(filename)

        with open(filename, 'r', encoding="utf-8", errors = 'ignore') as f:
            # print("MAIL NR " + str(ilość_maili))
            ilość_maili += 1
            for line in f:
                words = line.split()
                lista_słów.extend(words)
                # print(len(lista_słów))

    lista_słów = [x.lower() for x in lista_słów]

    słowa_na_maila = len(lista_słów) / ilość_maili

    for słowo in lista_słów:
        polskie_znaki = ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż']
        check = any(item in polskie_znaki for item in słowo)
        if check is False:
                słowo = re.sub('[^A-Za-z0-9]+', '', słowo)
        if check is True:
            słowo = re.sub('[!@#$()„:.,\'/?\-;\"”…_"]', '', słowo)

        if słowo not in częstotliwość_słów:
            częstotliwość_słów[słowo] = 1
        else:
            częstotliwość_słów[słowo] += 1

    for key, value in częstotliwość_słów.items():
        częstotliwość_słów[key] = value / ilość_maili
    return ilość_maili, słowa_na_maila, częstotliwość_słów

def do_pliku():

    ilość_spamu, długość_spamu, częstotliwość_słów_w_spamie = przegladanie_plikow("D:/Users/Marcin/PycharmProjects/FiltrowanieBayesa/wiadomości_spam")
    ilość_hamu, długość_hamu, częstotliwość_słów_w_hamie = przegladanie_plikow(r'D:\Users\Marcin\PycharmProjects\FiltrowanieBayesa\wiadomości')

    with open('D:/Users/Marcin/PycharmProjects/FiltrowanieBayesa/ham3.txt', "w", encoding="utf-8 ") as f:
        f.write(str(częstotliwość_słów_w_hamie))
    with open('D:/Users/Marcin/PycharmProjects/FiltrowanieBayesa/spam3.txt', "w", encoding="utf-8 ") as f:
        f.write(str(częstotliwość_słów_w_spamie))


#Funkcja ta była tylko używana do testów na gmailu,trzeba podac dane do swojego konta i poszperać w zabezpieczeniach imap
def read_email_from_gmail(poziom_filtrowania):
    ilość_spamu, długość_spamu, częstotliwość_słów_w_spamie = przegladanie_plikow("D:/Users/Marcin/PycharmProjects/FiltrowanieBayesa/wiadomości_spam")
    ilość_hamu, długość_hamu, częstotliwość_słów_w_hamie = przegladanie_plikow(r'D:\Users\Marcin\PycharmProjects\FiltrowanieBayesa\wiadomości')
    FROM_PWD =    ""                                                                                                                                          
    ORG_EMAIL = "@gmail.com"
    FROM_EMAIL = "dudududududux" + ORG_EMAIL
    SMTP_SERVER = "imap.gmail.com"
    SMTP_PORT = 993
    p_spam = 0
    p_ham = 0
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(FROM_EMAIL,FROM_PWD)
    mail.select('inbox')

    typ, data = mail.search(None, 'ALL')
    mail_ids = data[0]

    id_list = mail_ids.split()
    latest_email_id = int(id_list[-1])


    typ, data = mail.fetch(str(latest_email_id-3), "(UID BODY[TEXT])")    # Wybór maila,moze zmienic na innego niz tylko ostatni?

    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1].decode())
            email_subject = msg['subject']
            email_from = msg['from']
            raw_email = data[0][1].decode('utf-8')
            raw_email = str(raw_email)
    print(raw_email)
    raw = []

    for słowo in raw_email.split():
        raw.append(słowo)
        if '<div>' in słowo:
            start = (raw_email.split().index(słowo))
            słowo = słowo.replace('<div>', ' ')
            raw_email.split()[start] = słowo
        if '</div>' in słowo:
            end = (raw_email.split().index(słowo)) + 1
            słowo = słowo.replace('</div>', ' ')
        else:
            clean_mail = raw

    if clean_mail != raw:
        clean_mail = [słowo for słowo in raw_email.split()[start:end]]
        clean_mail[0] = clean_mail[0].replace('<div>', ' ')
        clean_mail[-1] = clean_mail[-1].replace('</div>', '')

    for słowo in clean_mail:
        print(słowo, end = ' ')
        if słowo not in częstotliwość_słów_w_hamie:
            częstotliwość_słów_w_hamie[słowo] = 0

        if słowo not in częstotliwość_słów_w_spamie:
            częstotliwość_słów_w_spamie[słowo] = 0

        szansa_w_spamie = częstotliwość_słów_w_spamie[słowo] / ilość_spamu
        szansa_w_hamie = częstotliwość_słów_w_hamie[słowo] / ilość_hamu

        ilość_maili = ilość_spamu + ilość_hamu
        ilość_maili = ilość_spamu + ilość_hamu
        if szansa_w_spamie != 0:
            p_spam += (szansa_w_spamie * ilość_spamu/ilość_maili)/((szansa_w_spamie * ilość_spamu/ilość_maili) + (szansa_w_spamie * ilość_spamu/ilość_maili) + (szansa_w_hamie * ilość_spamu/ilość_maili))
        if szansa_w_hamie !=0:
            p_ham += (szansa_w_hamie * ilość_hamu/ilość_maili)/((szansa_w_hamie * ilość_hamu/ilość_maili) + (szansa_w_hamie * ilość_hamu/ilość_maili) + (szansa_w_spamie * ilość_hamu/ilość_maili))

    p_ham,p_spam == p_ham/len(raw_email), p_spam/len(raw_email)


    if p_spam > poziom_filtrowania*p_ham:
        return 'spam'
    else:
        return 'ham'





#w = read_email_from_gmail(1)

#print(w)










def Sprawdz_maila(dir,poziom_filtrowania):
    ilość_spamu, długość_spamu, częstotliwość_słów_w_spamie = przegladanie_plikow("D:/Users/Marcin/PycharmProjects/FiltrowanieBayesa/wiadomości_spam")
    ilość_hamu, długość_hamu, częstotliwość_słów_w_hamie = przegladanie_plikow(r'D:\Users\Marcin\PycharmProjects\FiltrowanieBayesa\wiadomości')
    n = 1
    p_ham = 0
    p_spam = 0
    for filenames in os.listdir(dir):
        n += 1
        #print(dir)
        filename = dir + '\\' + filenames
        with open(filename, 'r') as f:
             for line in f:
                słowa = line.split()
                słowa = [x.lower() for x in słowa]
                for słowo in słowa:

                    if słowo not in częstotliwość_słów_w_hamie:
                        częstotliwość_słów_w_hamie[słowo] = 0

                    if słowo not in częstotliwość_słów_w_spamie:
                        częstotliwość_słów_w_spamie[słowo] = 0

                    szansa_w_spamie = częstotliwość_słów_w_spamie[słowo] / ilość_spamu
                    szansa_w_hamie = częstotliwość_słów_w_hamie[słowo] / ilość_hamu

                    ilość_maili = ilość_spamu + ilość_hamu
                    ilość_maili = ilość_spamu + ilość_hamu

                    if szansa_w_spamie != 0:
                        p_spam += (szansa_w_spamie * ilość_spamu / ilość_maili) / \
                                     ((szansa_w_spamie * ilość_spamu / ilość_maili) + (szansa_w_spamie * ilość_spamu / ilość_maili) +
                                         (szansa_w_hamie * ilość_spamu / ilość_maili))
                    if szansa_w_hamie != 0:
                        p_ham += (szansa_w_hamie * ilość_hamu / ilość_maili) / \
                                    ((szansa_w_hamie * ilość_hamu / ilość_maili) + (szansa_w_hamie * ilość_hamu / ilość_maili) +
                                        (szansa_w_spamie * ilość_hamu / ilość_maili))


    wzór = p_spam + poziom_filtrowania/5
    print(p_ham)
    print(wzór)
    if wzór > p_ham:
        return 'spam'
    else:
        return 'ham'
    return p_ham,p_spam


print(Sprawdz_maila("D:/Users/Marcin/PycharmProjects/FiltrowanieBayesa/do_sprawdzenia", 1))
do_pliku()