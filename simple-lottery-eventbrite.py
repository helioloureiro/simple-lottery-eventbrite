#! /usr/bin/env python3

from importlib import import_module
import random
from typing import Dict, List
from  http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import time
import csv
from dialog import Dialog
import sys

SOURCECODE = "https://github.com/helioloureiro/simple-lottery-eventbrite"

def generate_output_filename() -> str:
    '''
    dump the results in a file to use later (reach the winners)
    '''
    return time.strftime("lottery-result-%Y-%m-%d-%H:%M:%S.log")

class RunLottery:
    def __init__(self, csvfile):
        self.winners = []
        self.not_in_the_room = []
        self.csvfile = csvfile
        self.resultsLog = generate_output_filename()

        self.participants = self.generate_name_email_dict()

        self.participants_names = list(self.participants.keys())

    def generate_name_email_dict(self):
        name_email_dict = {}
        with open(self.csvfile, encoding='utf-8') as csvFile:
            csvreader = csv.DictReader(csvFile)
            for row in csvreader:
                fullName = row['Name']
                email = row['Email']
                if fullName in name_email_dict:
                    # raise Exception(f'The name {fullName} already exists')
                    print(f'{fullName} is already in the list')
                    continue
                name_email_dict[fullName] = email
                #print(f'Added {fullName} <{email}>')
        return name_email_dict

    def get_a_winner(self, listNames):
        '''
        It receives an array with name and picks one name randomly.
        Then verifies whether already in winners list or not in the room list.
        In case positive, adds the candidate into the winners list and returns result.
        '''
        while True:
            candidate = random.choice(listNames)
            if not candidate in self.winners and not candidate in self.not_in_the_room:
                self.winners.append(candidate)
                return candidate

    def dump_results(self):
        ''''
        Save the full name and email to reach the winners later.
        '''
        outputFilename = self.resultsLog
        with open(outputFilename, 'w') as dest:
            for fullName in self.winners:
                email = self.participants[fullName]
                dest.write(f'{fullName}, {email}\n')

    def protected_email(self, person):
        ''''
        To display the person's email, but not totally open.  Just the first
        5 characters.
        '''
        email = self.participants[person]
        protected = email[:5]
        for c in email[5:]:
            if c == '@':
                protected += c
            else:
                protected += '*'
        return protected

    def run(self):
        rounds = int(input('how many winners? '))
        for i in range(rounds):
            winner = self.get_a_winner(self.participants_names)
            safe_email = self.protected_email(winner)
            print(f'{i}) {winner} {safe_email}')
        self.dump_results()

    def run_dialog(self):
        ''''
        To run the lottery using dialog interface to confirm.
        '''
        dlg = Dialog(dialog="dialog")
        msg_width = len(SOURCECODE) + 4
        dlg.msgbox(f"Welcome to the simple lottery.\nSource code: {SOURCECODE} ", width=msg_width)

        rounds = 0
        while rounds == 0:
            code, result = dlg.inputbox("How many rounds?")
            if code == dlg.OK:
                try:
                    rounds = int(result)
                except ValueError:
                    pass

        dlg.msgbox(f"Running for {rounds} rounds")

        seed = 0
        while seed == 0:
            code, result = dlg.inputbox("Enter a number for seed random number generator")
            if code == dlg.OK:
                try:
                    seed = int(result)
                    random.seed(seed)
                except ValueError:
                    pass

        while rounds > 0:
            winner = self.get_a_winner(self.participants_names)
            email = self.protected_email(winner)
            code, tag = dlg.menu(f"{winner} <{email}>",
                        choices=[("[Ok]", "Person is in the room"),
                                ("[Try again]", "Not found, so let's try again")])
            if code == dlg.OK:
                if tag == "[Try again]":
                    # remove person
                    self.winners.remove(winner)
                    self.not_in_the_room.append(winner)
                if tag == "[Ok]":
                    rounds-=1
        dlg.msgbox(f"Saving result into {self.resultsLog}")
        self.dump_results()





def start_webserver():
    "src: https://www.programcreek.com/python/example/103649/http.server.BaseHTTPRequestHandler"
    print('not implemented yet')
    sys.exit(1)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html;charset=utf-8")
            self.end_headers()
            client_ip, client_port = self.client_address
            reqpath = self.path.rstrip()
            print(f"request from {client_ip}:{client_port} for {reqpath}")
            get_new_winner_button = f"""
            <center>
            <form action="/newwinner" method="get">
             <input type="submit" value="Run the lottery"><br />
             source code for audit: <a href="{SOURCECODE}">{SOURCECODE}</a>
            </form>
            </center>
            """
            if reqpath == "/newwinner?":
                save_line(article_selected)
                title = get_title(article_selected)
                link = get_link(article_selected)
                print("title:", title)
                print("article:", article_selected)
                response = f"""<title>{title}</title>
                <h1>Title: <a href="{link}">{title}</a></h1><br>
                <h2>Link: <a href="{link}">{link}</a></h2> """ + \
                get_new_winner_button
            else:
                response = get_new_winner_button
            content = bytes(response.encode("utf-8"))
            self.wfile.write(content)

    # Bind to the local address only.
    print("Starting webserver on port 8080")
    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="It uses an Eventbrite's CSV as input and generate an random lottery person")
    parser.add_argument("--web", action="store_true", help="It starts web interface (port 8080)")
    parser.add_argument("--dialog", action="store_true", help="It runs via dialog")
    parser.add_argument("--csvfile", help="Eventbrite's CSV attendant summary report")
    args = parser.parse_args()
    if args.csvfile is None:
        raise Exception("Missing --csvfile")

    if args.web:
        start_webserver()
        sys.exit(0)
    lottery = RunLottery(csvfile=args.csvfile)
    if args.dialog:
        lottery.run_dialog()
        sys.exit(0)
    lottery.run()