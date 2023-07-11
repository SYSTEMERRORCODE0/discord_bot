import openai
import discord
from discord.ext import commands

openai.api_key = ""
bot = commands.Bot(command_prefix=':(',intents=discord.Intents.all())

prompts = []
logs = []

chatType = "QnA"
# "QnA" : 간단한 질문답변 형식은 이것을 활성화 (토큰 소모 적음)
# "Chat" : 저장된 prompt만을 이용해서 사용할 경우 활성화 (토큰 소모 중간)
# "LearningChat" : 기존의 질문 답변도 반영해서 계속 하려면 활성화 (토큰 소모 심함)

def LoadLogs():
    
    f = open("ChatLog.txt", "r")

    rawStr = f.read()
    totalConv = rawStr.split("\n")
    logs = []
        
    for conv in totalConv:
        pair = conv.split(": ")
            
        keys = []
        values = []
            
        keys.append("role")
        values.append(pair[0])
        keys.append("content")
        values.append(pair[1])
            
        logs.append(dict(zip(keys, values)))
            
    f.close()

def LoadPrompts():
    global prompts

    f = open("ChatPrompt.txt", "r")
        
    rawStr = f.read()
    totalConv = rawStr.split("\n")
    prompts = []
        
    for conv in totalConv:
        pair = conv.split(": ")
            
        keys = []
        values = []
            
        keys.append("role")
        values.append(pair[0])
        keys.append("content")
        values.append(pair[1])
            
        prompts.append(dict(zip(keys, values)))
            
    f.close()

@bot.event
async def on_ready():
    print(f'Login bot: {bot.user}')

@bot.command()
async def 타입(message,*var):

    global chatType
    global logs
    global prompts

    if len(var) == 0:
        await message.channel.send(f"현재 타입 : {chatType}\n")
    elif var[0] == "QnA":
        chatType = "QnA"
        prompts = []
        await message.channel.send("QnA로 기능을 변경합니다.")
    elif var[0] == "Chat":
        chatType = "Chat"
        LoadPrompts()
        await message.channel.send("Chat으로 기능을 변경합니다.")
    elif var[0] == "LearningChat":
        chatType = "LearningChat"
        LoadPrompts()
        await message.channel.send("LearningChat으로 기능을 변경합니다. 다른 기능으로 변경/종료 전에 저장하시기를 권장합니다.")
    else:
        await message.channel.send(f"현재 타입 : {chatType}\n'QnA', 'Chat', 'LearningChat' 중 하나를 선택해주세요")

@bot.command()
async def 챗(message,*vars):

    global logs
    global prompts
    global chatType

    keys = []
    values = []

    keys.append("role")
    values.append("user")
    keys.append("content")
    str = " ".join(vars)
    values.append(str)

    prompt = dict(zip(keys, values))
    prompts.append(prompt)

    print(prompts)

    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=prompts,
        temperature=0.9,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )

    response = completion['choices'][0]['message']['content']
    await message.channel.send(response)
    print(response)

    if chatType == "Chat" or chatType == "QnA":
        del prompts[-1]

    keys = []
    values = []

    keys.append("role")
    values.append("assistent")
    keys.append("content")
    values.append(response)
    log = dict(zip(keys, values))
    
    logs.append(prompt)
    logs.append(log)
    

@bot.command()
async def 프롬프트저장(message):

    global prompts

    if chatType == "LearningChat":
        f = open("ChatPrompt.txt", "w")
        for prompt in prompts:
            f.write(f'{prompt["role"]}: {prompt["content"]}\n')
        f.close()
        await message.channel.send("Prompt를 저장 했습니다")
    else:
        await message.channel.send("LearningChat 타입일 때만 Prompt를 저장 가능합니다")

@bot.command()
async def 로그저장(message):

    global logs

    f = open("ChatLog.txt", "w")
    for log in logs:
        f.write(f'{role}: {content}\n')
    f.write(logs)
    f.close()
    await message.channel.send("채팅 로그를 저장 했습니다")

    
LoadLogs()
bot.run('')
    
