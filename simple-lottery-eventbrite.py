#! /usr/bin/env python3

import re
import random
from typing import Dict, List
from  http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import time
import html
import csv


save_output = False
output_filename = None

SOURCECODE = "https://github.com/helioloureiro/simple-lottery-eventbrite"

def generate_output_filename() -> str:
    return time.strftime("lottery-result-%Y-%m-%d-%H:%M:%S.log")
class RunLottery:
    def __init__(self, csvfile, outputFlag=False):
        self.winners = []
        self.csvfile = csvfile
        self.outputFlag = outputFlag
        self.resultsLog = generate_output_filename()

        self.participants = self.generate_name_email_dict()
        # print(participants)

        self.participants_names = list(self.participants.keys())

    def generate_name_email_dict(self):
        name_email_dict = {}
        with open(self.csvfile, encoding='utf-8') as csvFile:
            csvreader = csv.DictReader(csvFile)
            for row in csvreader:
                fullName = row['Name']
                email = row['Email']
                if fullName in name_email_dict:
                    raise Exception(f'The name {fullName} already exists')
                name_email_dict[fullName] = email
                print(f'Added {fullName} <{email}>')
        return name_email_dict

    def get_a_winner(self, listNames):
        while True:
            candidate = random.choice(listNames)
            if not candidate in self.winners:
                self.winners.append(candidate)
                return candidate

    def dump_results(self):
        outputFilename = generate_output_filename()
        with open(outputFilename, 'w') as dest:
            for fullName in self.winners:
                email = self.participants[fullName]
                dest.write(f'{fullName}, {email}\n')

    def protected_email(self, person):
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


def start_webserver():
    "src: https://www.programcreek.com/python/example/103649/http.server.BaseHTTPRequestHandler"
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
    parser.add_argument("--output", action="store_true", help="It enables to save results.")
    parser.add_argument("--csvfile", help="Eventbrite's CSV attendant summary report")
    args = parser.parse_args()
    if args.csvfile is None:
        raise Exception("Missing --csvfile")
    lottery = RunLottery(csvfile=args.csvfile, outputFlag=args.output)
    lottery.run()