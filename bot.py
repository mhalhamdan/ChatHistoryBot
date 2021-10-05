import discord
from datetime import datetime

TOKEN = 'token here'

client = discord.Client()

history_dict = {}

# Input datetime object
# Return time difference in either seconds, minutes, or hours, etc.
def find_time_diff(date_a, date_b):

    time_delta = (date_b - date_a)
    duration = time_delta.total_seconds()
    type = "seconds"

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

# discord.on_message_edit(before, after)

@client.event
async def on_message_edit(before, after):
    
    if before.id in history_dict.keys():
        # Format: current message.id : old message content
        # history_dict[before.id].append(f"{before.content} @ {after.edited_at}")
        history_dict[before.id].append((before.content, after.edited_at))
    else:
        history_dict[after.id] = [(before.content, after.edited_at)]

    

@client.event
async def on_message(message):

    if message.content == "-history":
        # Check if reply or not
        if message.reference is not None:
            message = await message.channel.fetch_message(message.reference.message_id) 

            if message.id in history_dict.keys():

                archive = history_dict[message.id]

                if len(archive) == 1:
                    return await message.reply(f"Message before edit: {archive[0][0]}")
                
                if len(archive) > 1:
                    response = "The message was edited more than once.\nThe complete message history is the following:\n"
                    for index, instance in enumerate(archive):
                        time_diff, type = find_time_diff(instance[1], datetime.utcnow())
                        response = f"{response}{index+1}-{instance[0]} @ {time_diff} {type} ago\n"
                    return await message.reply(response)


                
            else:
                return await message.reply("Selected message was not archived.")



        
client.run(TOKEN)