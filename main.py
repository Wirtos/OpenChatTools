import asyncio
from telethon import TelegramClient

# Telethon Errors
from telethon.errors import SessionPasswordNeededError, PeerIdInvalidError, \
    PhoneNumberInvalidError, PhoneCodeInvalidError, PasswordHashInvalidError, \
    PasswordEmptyError, FloodWaitError, UsernameNotModifiedError

# Full API functions
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.contacts import GetContactsRequest, DeleteContactsRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import DeletePhotosRequest, GetUserPhotosRequest

from re import match, IGNORECASE
from time import sleep
import datetime
from os import system, name as sysname
from sys import exit


# Simple animation with text on update callback
class Animate:
    def __init__(self, job_list, text=""):
        self.job_len = len(job_list)
        self.animation = '|/-\\'
        self.text = text
        self.job_counter = 0
        self.job_number = None

    def callback(self):
        self.job_counter += 1
        self.job_number = self.job_counter / self.job_len * 100
        print("{text}{percents}/100%{animation}".format(text=self.text,
                                                        percents=int(self.job_number),
                                                        animation=self.animation[self.job_counter % 4]), end="\r")


# Clear terminal
def cls():
    system('cls') if sysname == 'nt' else system('clear')


# Force floodwait if user reached requests limit
def flood_waiter(wait_time):
    timer = datetime.datetime.today()
    delta = timer + datetime.timedelta(seconds=wait_time)
    lock = delta - timer
    while lock.seconds > 0:
        timer = datetime.datetime.today()
        lock = delta - timer
        print("{} seconds remain".format(lock.seconds), end="\r")
        sleep(1)
    cls()


async def main():
    client = TelegramClient(None, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        try:
            phone_number = input("Phone number: {}".format(" " * 7))
            try:
                await client.send_code_request(phone=phone_number)
            except PhoneNumberInvalidError:
                print("-3, Phone number invalid")
                sleep(5)
                exit("-3")
            try:
                await client.sign_in(phone=phone_number, code=input('Enter telegram code: '))
            except PhoneCodeInvalidError:
                print("-2, Code invalid")
                sleep(5)
                exit("-2")
            except SessionPasswordNeededError:
                try:
                    await client.sign_in(password=input("2FA password: {}".format(" " * 7)))
                except (PasswordHashInvalidError, PasswordEmptyError):
                    print("-1, Password invalid")
                    sleep(5)
                    exit("-1")
        except FloodWaitError:
            print("Account login limited for 24 hours due login attempts flood.\nExiting...")
            sleep(5)
            exit("-5")
        cls()
    self_user = await client.get_me()
    print(
        """
first_name= [{0}]
last_name=  [{1}]
username=   [{2}]
id=         [{3}]
phone=      [{4}]
        """.format(self_user.first_name,
                   self_user.last_name,
                   self_user.username,
                   self_user.id,
                   self_user.phone)
    )
    answer = input("Clear account? \n(Y)es | (n)o\n")
    cls()
    if match(r'(y|yes)', answer, flags=IGNORECASE):
        dialogs = await client.get_dialogs()
        contacts_list = await client(GetContactsRequest(0))
        animation = Animate(dialogs, "1 of 3 - chats wiping: ")
        for _ in dialogs:
            animation.callback()
            try:
                sleep(0.5)
                try:
                    await client(DeleteHistoryRequest(_, 0))
                except PeerIdInvalidError:
                    await client(LeaveChannelRequest(_))
            except FloodWaitError as e:
                print("Telegram limits number of requests, please wait for {} seconds".format(e.seconds))
                print("When the limit passes, we will do everything ourselves\n")
                flood_waiter(e.seconds)
                try:
                    await client(DeleteHistoryRequest(_, 0))
                except PeerIdInvalidError:
                    await client(LeaveChannelRequest(_))

        del animation
        cls()
        animation = Animate(range(2), "1 of 3 - chats wiping: Done!\n2 of 3 - contacts wiping: ")
        for _ in range(2):
            animation.callback()
            try:
                sleep(0.5)
                await client(DeleteContactsRequest(contacts_list.users))
            except FloodWaitError as e:
                print("Telegram limits number of requests, please wait for {} seconds".format(e.seconds))
                print("When the limit passes, we will do everything ourselves\n")
                flood_waiter(e.seconds)
                await client(DeleteContactsRequest(contacts_list.users))

        del animation
        cls()
        print("""1 of 3 - chats wiping: Done!\n2 of 3 - contacts wiping: Done!\nName set to default\n\
Username cleared\nBio cleared\nProfile pics: Done!\n""")
        await client(UpdateProfileRequest(about="", first_name="default", last_name=""))
        try:
            await client(UpdateUsernameRequest(""))
        except UsernameNotModifiedError:
            pass
        me = await client.get_me()
        photos_list = await client(GetUserPhotosRequest(me, 0, 0, 0))
        await client(DeletePhotosRequest(photos_list.photos))
        input("Enjoy your brand-new account! (Press enter)")
        await client.log_out()
        exit("1")
    else:
        await client.log_out()
        exit("0")


if __name__ == '__main__':
    api_id = ""
    api_hash = ""

    if not api_id or not api_hash:
        raise AttributeError("Api hash and api id must be declared!")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
