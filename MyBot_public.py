import discord
import random
import youtube_dl
import asyncio
from discord.ext import commands

bot = commands.Bot(command_prefix=':(',intents=discord.Intents.all())

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

#CommandNotFoundError = 'Warning!! ": 해당하는 명령은 존재하지 않습니다.'
#VariablesError = 'Warning!! ": 해당하는 명령의 변수가 잘못되었습니다.'

Dicehelp = 'Commands\n:(주사위 N : 1부터 N까지 중 무작위 숫자 하나를 출력해줍니다.(N은 1 이상의 정수)'

@bot.event
async def on_ready():
    print(f'Login bot: {bot.user}')

@bot.command()
async def test(message):
    await message.channel.send('Hello?')
    print(f'Reply for "test" -> "Hello?"')

@bot.command() #not working now
async def embedtest(message):
    await message.channel.send("werwer",embed=Embed("werw"))
    print(f'Reply for "test" -> "Hello?"')

###################

@bot.command()
async def 주사위(message,*vars):
    
    if(len(vars)==0):
        await message.channel.send(Dicehelp)
        
    elif(len(vars)==1):
        if(vars[0]=="help"):
            await message.channel.send(Dicehelp)
        elif(vars[0].isdecimal() and int(vars[0]) > 0):
            n = random.randrange(1,int(vars[0])+1)
            await message.channel.send(f'주사위 결과 : {n}')

    reply = ' '.join(vars)
    print(f'Reply for "주사위 {reply}')

####################
# 노래틀기
#
# youtube_dl reference : https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl

playList = []
playNumber = 0
voiceChannel = None
messageChannel = None
songSkip = 0

ydl_opts = {
    'quiet': False,
    'default_search': 'ytsearch',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'youtube_include_dash_manifest': False,
} # 비어있으면 일반 영상 형태

FFMPEG_OPTIONS = {
    'executable': 'C:/ffmpeg-5.1.2-full_build/bin/ffmpeg.exe',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
} #ffmpeg를 https://www.gyan.dev/ffmpeg/builds/ 에서 다운로드 및 설치, executable에서 경로 지정

def my_after(error):
    try:
        fut = None
        if playNumber < len(playList):
            fut = asyncio.run_coroutine_threadsafe(play_list(bot.voice_clients[0]), bot.loop)
            fut.result()
        #elif playNumber == len(playList):
            
            
    except Exception as e:
        print(e)

async def play_list(voice):
    global playNumber
    global messageChannel
    
    try:
        info = playList[playNumber]
        await messageChannel.send(f"현재 재생 곡\n"
                                  f"제목 : {info['title']}\n"
                                  f"영상 길이 : {info['duration']//60}분 {info['duration']%60}초\n"
                                  f"URL : {info['webpage_url']}")
        url = info['formats'][0]['url']
        playNumber = playNumber + 1
        voice.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after = my_after)
    except Exception as e:
        print(e)

@bot.command()
async def play(message,*vars):

    global voiceChannel
    global messageChannel
    global playNumber
    voiceChannel = message.author.voice.channel
    messageChannel = message.channel
    
    if len(bot.voice_clients) == 0:
        await voiceChannel.connect()
        await messageChannel.send("봇이 노래 틀려고 입장했습니다")

    if not message.channel == messageChannel:
        return 1
        
    voice = bot.voice_clients[0]
    
    if len(vars) == 0:
        if len(playList) <= playNumber:
            await messageChannel.send("플레이리스트 끝이거나, 비어있습니다")
        elif voice.is_playing():
            await messageChannel.send("노래가 이미 재생중입니다")
        elif voice.is_paused():
            await voice.resume()
        else:
            await play_list(voice)

    elif len(vars) == 1 and vars[0].isdecimal():
        playNumber = int(vars[0])
        bot.voice_clients[0].stop()

    else :
        str = " ".join(vars)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if str[0:23] == "https://www.youtube.com" or str[0:16] == "https://youtu.be":
                info = ydl.extract_info(str, download = False)
            else:
                info = ydl.extract_info(f"ytsearch:{str}", download = False)['entries'][0]
            await messageChannel.send(f"다음 곡을 큐에 추가했습니다\n"
                                      f"제목 : {info['title']}\n"
                                      f"영상 길이 : {info['duration']//60}분 {info['duration']%60}초\n"
                                      f"URL : {info['webpage_url']}")
            playList.append(info)
        #await messageChannel.send("다음 곡을 큐에 추가했습니다")
        if voice.is_paused():
            await messageChannel.send("큐에 노래를 추가했지만, 노래 재생은 멈춘 상태입니다. :(play 나 :(resume 으로 재생해주세요")
        elif voice.is_playing() == False:
            await play_list(voice)
            

    #elif(len(vars)==1):        
    #    if(vars[0]==""):


@bot.command()
async def stop(message):
    global messageChannel
    if message.channel == messageChannel:
        await bot.voice_clients[0].disconnect()
        await message.channel.send("NAGA")

@bot.command()
async def leave(message):
    global messageChannel
    if message.channel == messageChannel:
        await bot.voice_clients[0].disconnect()
        await message.channel.send("NAGA")

@bot.command()
async def reset(message):
    global messageChannel
    if message.channel == messageChannel:
        bot.voice_clients[0].stop()
        global playNumber
        playNumber = 0
        playList.clear()
        await message.channel.send("큐를 초기화했습니다")

@bot.command()
async def pause(message):
    global messageChannel
    if message.channel == messageChannel:
        bot.voice_clients[0].pause()
        await message.channel.send("노래를 일시정지했습니다")

@bot.command()
async def resume(message):
    global messageChannel
    if message.channel == messageChannel:
        bot.voice_clients[0].resume()
        await message.channel.send("노래를 계속 재생합니다")

@bot.command()
async def queue(message,*vars):
    global playNumber
    global messageChannel
    queueIdx = playNumber - 1
    if len(vars) > 0 and vars[0].isdecimal():
        queueIdx = int(vars[0])
    if message.channel == messageChannel:
        plist = []
        for i in range(max(0,queueIdx-5),min(len(playList),queueIdx+5)):
            if i == playNumber - 1:
                plist.append("현재 진행 곡 ↓")
            plist.append(f"{i} : {playList[i]['title']} / {playList[i]['duration']//60}분 {playList[i]['duration']%60}초")
        embed = discord.Embed(title="Play List Queue", description="\n".join(plist), color=0xFF5733)
        await message.channel.send(embed=embed)

@bot.command()
async def delete(message,*vars):
    global playNumber
    global messageChannel
    idx = playNumber - 1
    if len(vars) > 0 and vars[0].isdecimal():
        idx = int(vars[0])
    if idx >= len(playList):
        await message.channel.send("해당하는 노래가 없습니다")
        return 1
    if message.channel == messageChannel:
        if idx < playNumber:
            playNumber = playNumber - 1
        await message.channel.send(f"삭제한 곡 인덱스 {idx} : {playList[idx]['title']} / {playList[idx]['duration']//60}분 {playList[idx]['duration']%60}초\n")
        del playList[idx]

@bot.command()
async def skip(message):
    global messageChannel
    if message.channel == messageChannel:
        bot.voice_clients[0].stop()
        await message.channel.send("현재 노래를 스킵합니다")

@bot.command()
async def 나가(message):
    await bot.change_presence(status=discord.Status.offline) #오프라인

@bot.command()
async def 들어와(message):
    await bot.change_presence(status=discord.Status.online) #온라인

@bot.command()
async def 뭐함(message):
    game = discord.Game("낚시")
    await bot.change_presence(status=discord.Status.online,activity=game) #온라인

bot.run('DISCORD API KEY HERE')

