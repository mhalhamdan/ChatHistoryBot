import discord
from datetime import datetime
import datetime as dt
import json

TOKEN = 'token here'

client = discord.Client()

# RESET_THRESHOLD = 1000
TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

SECONDS_DICTIONARY = {
    "seconds": 1,
    "minutes": 60,
    "hours": 3600,
    "days": 3600*24
}

def round_seconds(time):
    x = time - dt.timedelta(microseconds=time.microsecond)
    return x


class History(object):

    history_dict = {}

    def __init__(self):
        self.history_dict = {}

    def save_history(self):
        with open('history.json', 'w') as fp:
            json.dump(self.history_dict, fp)

    def load_history(self):
        with open('history.json', 'r') as fp:
            self.history_dict = json.load(fp)

history = History()

try:
    history.load_history()
except:
    print("ERROR: Couldn't load history")
    
# Input datetime object
# Return time difference in either seconds, minutes, or hours, etc.
def find_time_diff(date_a, date_b, enforce_type=False):

    time_delta = date_b - date_a
    duration = time_delta.total_seconds()
    type = "seconds"

    if enforce_type:
        duration /= SECONDS_DICTIONARY[enforce_type]
        return round(duration, 2), enforce_type

    # If larger, convert for better visualization
    if duration > 60: # s -> m
        duration /= 60
        type = "minutes"
        if duration > 60: # m -> h
            duration /= 60
            type = "hours"
            if duration > 24: # h -> d
                duration /= 24
                type = "days"
    
    return round(duration, 2), type

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message_delete(message):

    deleted_time = datetime.utcnow()

    if str(message.author.id) in history.history_dict.keys():
        # Format: current message.id : old message content
        history.history_dict[str(message.author.id)].append((message.content, str(deleted_time)))
        history.save_history()
    else:
        history.history_dict[str(message.author.id)] = [(message.content, str(deleted_time))]
        history.save_history()

@client.event
async def on_message_edit(before, after):
    
    if str(before.id) in history.history_dict.keys():
        # Format: current message.id : old message content
        history.history_dict[str(before.id)].append((before.content, str(after.edited_at)))
        history.save_history()
    else:
        history.history_dict[str(after.id)] = [(before.content, str(after.edited_at))]
        history.save_history()


@client.event
async def on_message(message):

    if message.content[:8] == "-history":
        # Check if reply or not
        if message.reference is not None:
            message = await message.channel.fetch_message(message.reference.message_id) 

            if str(message.id) in history.history_dict.keys():

                archive = history.history_dict[str(message.id)]

                if len(archive) == 1:
                    return await message.reply(f"Message before edit: {archive[0][0]}")
                
                if len(archive) > 1:
                    response = "The message was edited more than once.\nThe complete message history is the following:\n"
                    for index, instance in enumerate(archive):
                        time_diff, type = find_time_diff(datetime.strptime(instance[1], TIME_FORMAT), datetime.utcnow())
                        response = f"{response}{index+1}-{instance[0]} @ {time_diff} {type} ago\n"
                    return await message.reply(response)
            else:
                return await message.reply("Selected message was not archived.")

        # Check for correct arguments
        content = message.content.split()
        if len(content) != 3:
            return await message.channel.send("The correct arguments are: -history <user> <no. of hours>")

        # If references an author, to find deleted messages
        elif (content[1].strip("<").strip(">").strip("@").strip("!")) in history.history_dict.keys():
            archive = history.history_dict[(content[1].strip("<").strip(">").strip("@").strip("!"))]
            print(archive)
            if len(archive) == 1:
                return await message.reply(f"User has one deleted message: {archive[0][0]}")

            # Reverse archive to iterate from the most recent message
            archive.reverse()

            if len(archive) > 1:
                response = f"User deleted the following messages in the past {content[2]} hour:\n"
                # In seconds
                THRESHOLD = int(content[2])*3600

                for index, instance in enumerate(archive):
                    time_diff, type = find_time_diff(datetime.strptime(instance[1], TIME_FORMAT), datetime.utcnow())
                    
                    compare = THRESHOLD / SECONDS_DICTIONARY[type]

                    if time_diff > compare:
                        break 
                    response = f"{response}{index+1}-{instance[0]} @ {time_diff} {type} ago\n"

                return await message.reply(response)

        
client.run(TOKEN)