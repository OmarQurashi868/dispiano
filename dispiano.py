import discord
import pysynth as psb
import sys
import asyncio


client = discord.Client()
command_lock = asyncio.Lock()


def parse_client_message_content(message):
    tokens = message.split()
    # Strip the "!piano"
    tokens = tokens[1:]

    bpm = 110

    try:
        bpm = int(tokens[0])
        tokens = tokens[1:]
    except:
        pass

    bpm = max(30, min(800, bpm))

    song = []

    for token in tokens:
        note = token
        length = 4
        if ',' in token:
            parts = token.split(',')
            note = parts[0].lower()
            length = float(parts[1])
        song.append((note.lower(), length))

    return (song, bpm)


@client.event
async def on_message(message):
    if message.content.startswith('!piano'):
        await command_lock.acquire()
        if message.author.voice.voice_channel is None:
            await client.send_message(
                message.channel,
                'Hey dumb dumb! ' +
                'You need to be in a voice channel to use this bot.')
            return

        try:
            song, bpm = parse_client_message_content(message.content)
        except:
            await client.send_message(
                message.channel,
                'Hey dumb dumb! ' +
                'Your notes are malformed!')
            command_lock.release()
            return

        try:
            psb.make_wav(song, fn="out.wav", bpm=bpm)
        except:
            await client.send_message(
                message.channel,
                'Hey dumb dumb! ' +
                'Your notes are malformed!')
            command_lock.release()
            return

        try:
            voice = await client.join_voice_channel(
                message.author.voice.voice_channel)

            player = voice.create_ffmpeg_player('out.wav')
            player.start()

            while not player.is_done():
                await asyncio.sleep(1)
        finally:
            await voice.disconnect()
            command_lock.release()

def main():
    if len(sys.argv) == 2:
        token = sys.argv[1]
        client.run(token)
    else:
        print("Error: must pass in your bot's token as a command line argument!")


if __name__ == "__main__":
    main()
