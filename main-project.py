from typing import Optional
import discord
import os
from discord.ext import commands, voice_recv
from urllib.request import urlretrieve
import requests
import io
import PyPDF2
import fakeyou
from openai import OpenAI
import ctypes
import asyncio
import boto3
import mysql.connector as sqltor
#------------------------------------------------

discord.opus.load_opus("/opt/homebrew/Cellar/opus/1.4/lib/libopus.dylib") 
discordtoken=""
gptclient = OpenAI(api_key="")
fy=fakeyou.FakeYou()
fy.login("","")
mycon=sqltor.connect(host="",user="", passwd="",database="")
if mycon.is_connected():
    print('Succesfully Connected to MySql')
cursor=mycon.cursor()

#cursor.execute("CREATE TABLE celebelum (id numeric(23) NOT NULL, name varchar(100) NOT NULL, points varchar (2), subject varchar (23));")




def fakeu(celebid):
  a=fy.say(text="Correct",ttsModelToken=celebid)
  a.save(f"true.wav")
  a=fy.say(text="Wrong. Try Next Question",ttsModelToken=celebid)
  a.save(f"false.wav")
  a=fy.say(text="Thanks For Participating",ttsModelToken=celebid)
  a.save(f"thanks.wav")
#------------------------------------------------

client = commands.Bot(command_prefix=['Ptz.','ptz.','p.','P.'], intents=discord.Intents.all())
client.remove_command("help")

@client.event
async def on_ready():
  print ('We have logged in as {0.user}' .format (client))
  await client.wait_until_ready()
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
  await client.tree.sync()

#------------------------------------------------
def gptresponse(reader,command,pagenumber):
      conversation = [{"role":"system", "content":"You are master tutor and all of your students get great grades because of you. Concise the text that is given to you and make it useful for the students. All important facts and details should remain. Also give 10 questions as a quiz. These should only have true or false as an answer. Mention the answer too in brackets after the question. DO NOT LEAVE any important info. Make it below 500 characters."}]
      conversation.append({"role":"user","content":'Here is the text'+str(reader.pages[pagenumber].extract_text())+'make the summary and quiz'})
      GPTresponse = gptclient.chat.completions.create(
      model="gpt-4",
      messages=conversation)
      conversation.pop()
      stringfinal = GPTresponse.choices[0].message.content
      if command=="celebs":
         return stringfinal
      elif command=="translate":
        target_language_code="hi"
        stringfinal = translate_text(stringfinal, target_language_code)
        return stringfinal

async def summary(content,vc,command,gpt,celebid,subject):
  if command=="celebs":
    summary = gpt.split('Quiz')[0]
    a=fy.say(text=f"{summary}",ttsModelToken=celebid)
    a.save(f"summary.wav")
    vc.play(discord.FFmpegPCMAudio("summary.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(quiz(content,vc,0,gpt,celebid,subject), client.loop))
  elif command=="translate":
    response = gptclient.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=f"{gpt}",)
    response.write_to_file("output.wav")
    vc.play(discord.FFmpegPCMAudio("output.wav"))


async def image(summary):   
  response = gptclient.images.generate(
    model="dall-e-3",
    prompt=f"{summary}",
    size="1024x1024",
    quality="standard",
    n=1,
  )
  image_url = response.data[0].url
  return image_url

async def playquestion(content,vc,question,quiz_list,gpt,celebid):
  vc.stop_playing()
  a=fy.say(text=f"{quiz_list[question]['question']}",ttsModelToken=celebid)
  a.save(f"question{question}.wav")
  vc.play(discord.FFmpegPCMAudio(f"question{question}.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(quiz(content,vc,question,gpt,celebid), client.loop))

async def quiz(content,vc,question,gpt,celebid,subject):
    vc.stop_playing()
    if question<=10:
      print("testing")
      quiz_text = gpt.split("Quiz:")[1]
      quiz_dict = quiz_text_to_dict(quiz_text)
      quiz_list = list(quiz_dict.values())
      print(quiz_list)
      print(question)
      #to getover slow internet and audio packets braking along the way
      if question<=9:
          text=input("Enter true/false/start: ")
          print(text)
      if text.lower()=="start" and question==0:
              print("#1")
              a=fy.say(text=f"{quiz_list[0]['question']}",ttsModelToken=celebid)
              print("#2")
              a.save(f"question1.wav")
              print("#3")
              vc.play(discord.FFmpegPCMAudio("question1.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(quiz(content,vc,1,gpt,celebid), client.loop))
      elif text.lower()=="true" and question>=1:
              if str(quiz_list[question]['answer']).lower()==text.lower():
                print(str(quiz_list[question]['answer']).lower())
                print(text.lower())
                vc.play(discord.FFmpegPCMAudio("true.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt,celebid), client.loop))
              else:
                print(str(quiz_list[question]['answer']).lower())
                print(text.lower())
                vc.play(discord.FFmpegPCMAudio("false.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt,celebid), client.loop))       
      elif text.lower()=="false" and question>=1:
              if str(quiz_list[question]['answer']).lower()==text.lower():
                vc.play(discord.FFmpegPCMAudio("true.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt,celebid), client.loop))
              else:
                vc.play(discord.FFmpegPCMAudio("false.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt,celebid), client.loop))
      #comment the above code and un-comment below to test working model
    #   if question==0:
    #     a=fy.say(text=f"{quiz_list[0]['question']}",ttsModelToken=celebid)
    #     a.save(f"question1.wav")      
    #   def cb(celebid,user, text: str):
    #       print("entered")
    #       if question<=9:
    #         if text.lower()=="start" and question==0:
    #             vc.stop_listening()
    #             vc.play(discord.FFmpegPCMAudio("question1.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(quiz(content,vc,1,gpt,celebid), client.loop))
    #         elif text.lower()=="true" and question>=1:
    #             vc.stop_listening()
    #             if str(quiz_list[question]['answer']).lower()==text.lower():
    #               vc.play(discord.FFmpegPCMAudio("true.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt,celebid), client.loop))
    #             else:
    #               vc.play(discord.FFmpegPCMAudio("false.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt,celebid), client.loop))       
    #         elif text.lower()=="false" and question>=1:
    #             vc.stop_listening()
    #             if str(quiz_list[question]['answer']).lower()==text.lower():
    #               vc.play(discord.FFmpegPCMAudio("true.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt,celebid), client.loop))
    #             else:
    #               vc.play(discord.FFmpegPCMAudio("false.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt,celebid), client.loop))
    #   vc.listen(voice_recv.UserFilter(voice_recv.extras.SpeechRecognitionSink(text_cb=cb(),phrase_time_limit=5),content.user))        
    # else:
    #     myEmbed = discord.Embed(title="Celebelum", description="**CELEBRITY-AI STUDY TOOL \n REPORT", color=0x00ff00)
    #     await content.response.send_message(embed=myEmbed)

def quiz_text_to_dict(quiz_text):
    quiz_dict = {}
    for line in quiz_text.strip().split("\n"):
        question, answer = line.rsplit(" (", 1)
        question_number = int(question.split(". ", 1)[0])
        question_text = question.split(". ", 1)[1]
        answer = answer.replace("(", "").replace(")", "").strip()
        answer_bool = True if answer == "True" else False
        quiz_dict[question_number] = {"question": question_text, "answer": answer_bool}
    return quiz_dict

def translate_text(text, target_language, source_language='en'):
    
    try:
        translate = boto3.client(service_name='translate', aws_access_key_id='',
                                 aws_secret_access_key='',
                                 region_name='us-east-1')
        result = translate.translate_text(Text=text,
                                          SourceLanguageCode=source_language,
                                          TargetLanguageCode=target_language)
                                          
        return result.get('TranslatedText')
    except Exception as e:
        print(f"An error occurred during translation:{e}")
        return None

#------------------------------------------------
        
@client.tree.command(name="help", description="Help command.")
async def help(content: discord.Interaction):
    myEmbed = discord.Embed(title="Celebelum", description="**CELEBRITY-AI STUDY TOOL**\n\nCreate a profile 👤: </profile:1170722473633919026>\n Learn From Celebrity 🍎: </diet:1170569290072719502>\n Learn In Foreign Language 👨‍⚕️: </finddocs:1170612893314727967>\n Delete profile ❌: </deleteprofile:1170539459134107660>\n Report & Leaderboard 🏆: </leaderboard:1170619099810889818>", color=0x00ff00)
    await content.response.send_message(embed=myEmbed)

#------------------------------------------------
    
@client.tree.command(name="celeb", description="Hear the pdf summary and quiz yourself")
@commands.cooldown(1,5,commands.BucketType.user)
@discord.app_commands.choices(celebs=
                              [discord.app_commands.Choice(name="Millie Bobby Brown", value="TM:edsa15q98zmy"),
                               discord.app_commands.Choice(name="Donald Trump", value="TM:03690khwpsbz"),
                               discord.app_commands.Choice(name="Andrew Tate", value="TM:43c7p13p3z5c"),
                               discord.app_commands.Choice(name="MrBeast", value="TM:r1jbtkgnc6ep"),
                               ])
@discord.app_commands.choices(subject=
                              [discord.app_commands.Choice(name="Math", value="1S"),
                               discord.app_commands.Choice(name="English", value="2S"),
                               discord.app_commands.Choice(name="History", value="3S"),
                               discord.app_commands.Choice(name="Biology", value="4S"),
                               ])
async def celeb(content: discord.Interaction,book:discord.Attachment,celebs:discord.app_commands.Choice[str],pagenumber:int,subject:discord.app_commands.Choice[str]):
    await content.response.defer(ephemeral=True)
    fakeu(celebs.value)
    if content.user.voice != None:
        #---------------------------------
        buffer = io.BytesIO()
        await book.save(buffer)
        buffer.seek(0)
        reader = PyPDF2.PdfReader(buffer)
        #---------------------------------
        vc = await content.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        gpt=gptresponse(reader,"celebs",pagenumber)
        #---------------------------------
        myEmbed = discord.Embed(title="Celebelum", description="Your Celebrity AI Assistant",color=0x00ff00)
        summarypost = gpt.split('Quiz')[0]
        myEmbed.add_field(name="", value =f"{summarypost}", inline=False)
        quiz_text = gpt.split("Quiz:")[1]
        quiz_dict = quiz_text_to_dict(quiz_text)
        temp="Questions:\n"
        for a in quiz_dict.values():
          temp=temp+a['question']+"\n"
        myEmbed.add_field(name="", value =f"{temp}", inline=False)
        a=await image(gpt)
        myEmbed.set_image(url=f"{a}")
        vc.play(discord.FFmpegPCMAudio("intro.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(summary(content,vc,"celebs",gpt,celebs.value,subject.name), client.loop))
        await content.followup.send(embed=myEmbed)

#-----------------------------------------------
        
@client.tree.command(name="translate", description="Translated pdf summary and quiz")
@commands.cooldown(1,5,commands.BucketType.user)
async def score(content: discord.Interaction,book:discord.Attachment,pagenumber:int):
    await content.response.defer(ephemeral=True)
    if content.user.voice != None:
        #---------------------------------
        buffer = io.BytesIO()
        await book.save(buffer)
        buffer.seek(0)
        reader = PyPDF2.PdfReader(buffer)
        #---------------------------------
        command="translate"
        vc = await content.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.play(discord.FFmpegPCMAudio("intro.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(summary(content,vc,reader,command,"0"), client.loop))
        #---------------------------------
        myEmbed = discord.Embed(title="Bot", description="hi", color=0x00ff00)
        await content.followup.send(embed=myEmbed)


#------------------------------------------------
@client.tree.command(name="report", description="Compiled report")
@commands.cooldown(1,5,commands.BucketType.user)
@discord.app_commands.choices(reports=
                              [discord.app_commands.Choice(name="Quiz Performance", value="1R"),
                               discord.app_commands.Choice(name="Overall Performance In Different Subject", value="2R"),
                               discord.app_commands.Choice(name="Leaderboard", value="3R"),
                               ])
async def report(content: discord.Interaction, reports:discord.app_commands.Choice[str]):
    await content.response.defer(ephemeral=True)
    myEmbed = discord.Embed(title="Celebelum", description="Your Celebrity AI Assistant",color=0x00ff00)
    if reports.value=="1R":
      file = discord.File("/Users/dhawalarora/Desktop/Projects/Hackathon Projects/3.jpeg", filename="3.jpeg")
      myEmbed.set_image(url="attachment://3.jpeg")
    elif reports.value=="2R":
      file = discord.File("/Users/dhawalarora/Desktop/Projects/Hackathon Projects/2.jpeg", filename="2.jpeg")
      myEmbed.set_image(url="attachment://2.jpeg") 
    else:
      file = discord.File("/Users/dhawalarora/Desktop/Projects/Hackathon Projects/1.jpeg", filename="1.jpeg")
      myEmbed.set_image(url="attachment://1.jpeg") 
    await content.followup.send(file=file,embed=myEmbed)

client.run(discordtoken)