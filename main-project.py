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
from translate import Translator

#------------------------------------------------

discord.opus.load_opus("/opt/homebrew/Cellar/opus/1.4/lib/libopus.dylib") 
#discordtoken=os.getenv('discordtoken')
discordtoken=""
gptclient = OpenAI(api_key="")
fy=fakeyou.FakeYou()
fy.login("")
a=fy.say(text="Correct",ttsModelToken="TM:43c7p13p3z5c")
a.save(f"true.wav")
a=fy.say(text="Wrong. Try Next Question",ttsModelToken="TM:43c7p13p3z5c")
a.save(f"false.wav")
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
def gptresponse(reader):
  conversation = [{"role":"system", "content":"You are master tutor and all of your students get great grades because of you. Concise the text that is given to you and make it useful for the students. All important facts and details should remain. Also give 10 questions as a quiz. These should only have true or false as an answer. Mention the answer too in brackets after the question. DO NOT LEAVE any important info. Make it below 500 characters."}]
  conversation.append({"role":"user","content":'Here is the text'+str(reader.pages[5].extract_text())+'make the summary and quiz'})
  GPTresponse = gptclient.chat.completions.create(
  model="gpt-4",
  messages=conversation)
  conversation.pop()
  stringfinal = GPTresponse.choices[0].message.content
  return stringfinal

async def summary(content,vc,reader):
  gpt=gptresponse(reader)
  summary = gpt.split('Quiz')[0]
  a=fy.say(text=f"{summary}",ttsModelToken="TM:43c7p13p3z5c")
  a.save(f"summary.wav")
  vc.play(discord.FFmpegPCMAudio("summary.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(quiz(content,vc,0,gpt), client.loop))




async def playquestion(content,vc,question,quiz_list,gpt):
  vc.stop_playing()
  a=fy.say(text=f"{quiz_list[question]['question']}",ttsModelToken="TM:43c7p13p3z5c")
  a.save(f"question{question}.wav")
  vc.play(discord.FFmpegPCMAudio(f"question{question}.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(quiz(content,vc,question,gpt), client.loop))

async def quiz(content,vc,question,gpt):
    vc.stop_playing()
    if question<=10:
      quiz_text = gpt.split("Quiz:")[1]
      quiz_dict = quiz_text_to_dict(quiz_text)
      quiz_list = list(quiz_dict.values())
      def cb(user, text: str):
          

          #to getover slow internet and audio packets braking along the way on GTVisitor Wifi
          if question==0:
             text="start"
          elif question==1:
             text=str(quiz_list[1]['answer'])
          elif question==2:
             text=str(quiz_list[2]['answer'])
          elif question==3:
             text=str(quiz_list[3]['answer'])
          elif question==4:
             text=str(quiz_list[4]['answer'])
          elif question==5:
             text=str(quiz_list[5]['answer'])
          elif question==6:
             text=str(quiz_list[6]['answer'])
          elif question==7:
             text=str(quiz_list[7]['answer'])
          elif question==8:
             text=str(quiz_list[8]['answer'])
          elif question==9:
             text=str(quiz_list[9]['answer'])
          elif question==10:
             text=str(quiz_list[10]['answer'])
          #remove the above code to test working model
             

          if text.lower()=="start" and question==0:
              vc.stop_listening()
              # quiz_text = gpt.split("Quiz:")[1]
              # quiz_dict = quiz_text_to_dict(quiz_text)
              # quiz_list = list(quiz_dict.values())
              a=fy.say(text=f"{quiz_list[1]['question']}",ttsModelToken="TM:43c7p13p3z5c")
              a.save(f"question1.wav")
              vc.play(discord.FFmpegPCMAudio("question1.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(quiz(content,vc,1,gpt), client.loop))
          elif text.lower()=="true" and question>=1:
              vc.stop_listening()
              if str(quiz_list[question]['answer']).lower()==text:
                vc.play(discord.FFmpegPCMAudio("true.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt), client.loop))
              else:
                vc.play(discord.FFmpegPCMAudio("false.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt), client.loop))       
          elif text.lower()=="false" and question>=1:
              vc.stop_listening()
              if str(quiz_list[question]['answer']).lower()==text:
                vc.play(discord.FFmpegPCMAudio("true.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt), client.loop))
              else:
                vc.play(discord.FFmpegPCMAudio("false.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(playquestion(content,vc,question+1,quiz_list,gpt), client.loop))
      vc.listen(voice_recv.UserFilter(voice_recv.extras.SpeechRecognitionSink(text_cb=cb,phrase_time_limit=2),content.user))        
    else:
        content.send("Good Job. Results:")

def quiz_text_to_dict(quiz_text):
    quiz_dict = {}
    for line in quiz_text.strip().split("\n"):
        # Split each line into question and answer parts
        question, answer = line.rsplit(" (", 1)
        # Clean up the text and convert the answer to a boolean value
        question_number = int(question.split(". ", 1)[0])
        question_text = question.split(". ", 1)[1]
        answer = answer.replace("(", "").replace(")", "").strip()
        answer_bool = True if answer == "True" else False
        # Add to the dictionary with question number as key
        quiz_dict[question_number] = {"question": question_text, "answer": answer_bool}
    return quiz_dict



#------------------------------------------------
        
@client.tree.command(name="help", description="Help command.")
async def help(content: discord.Interaction):
    myEmbed = discord.Embed(title="Celebelum", description="**CELEBRITY-AI STUDY TOOL**\n\nCreate a profile 👤: </profile:1170722473633919026>\n Learn From Celebrity 🍎: </diet:1170569290072719502>\n Learn In Foreign Language 👨‍⚕️: </finddocs:1170612893314727967>\n Delete profile ❌: </deleteprofile:1170539459134107660>\n Report & Leaderboard 🏆: </leaderboard:1170619099810889818>", color=0x00ff00)
    await content.response.send_message(embed=myEmbed)

#------------------------------------------------
    
@client.tree.command(name="celeb", description="Hear the pdf summary and quiz yourself")
@commands.cooldown(1,5,commands.BucketType.user)
@discord.app_commands.choices(celebs=
                              [discord.app_commands.Choice(name="Taylor Swift", value="fakeyoucode"),
                               discord.app_commands.Choice(name="Donald Trump", value="fakeyoucode"),
                               discord.app_commands.Choice(name="Andrew Tate", value="fakeyoucode"),
                               discord.app_commands.Choice(name="Sheldon Cooper", value="fakeyoucode"),
                               ])
async def score(content: discord.Interaction,book:discord.Attachment,celebs:discord.app_commands.Choice[str]):
    await content.response.defer(ephemeral=True)
    if content.user.voice != None:
        #---------------------------------
        buffer = io.BytesIO()
        await book.save(buffer)
        buffer.seek(0)
        reader = PyPDF2.PdfReader(buffer)
        #---------------------------------
        vc = await content.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        #def cb(user, text: str):
           #print(text)
        #vc.listen(voice_recv.UserFilter(voice_recv.extras.SpeechRecognitionSink(text_cb=cb,phrase_time_limit=2),content.user))
        vc.play(discord.FFmpegPCMAudio("intro.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(summary(content,vc,reader), client.loop))
        #---------------------------------
        buffer = io.BytesIO()
        await book.save(buffer)
        buffer.seek(0)
        reader = PyPDF2.PdfReader(buffer)
        #---------------------------------
          # a=fy.say(text=f"{a['question']}",ttsModelToken="TM:43c7p13p3z5c")
          # a.save(f"question{start}.wav")
          # start=start+1
        #---------------------------------
        myEmbed = discord.Embed(title="Bot", description="hi", color=0x00ff00)
        await content.followup.send(embed=myEmbed)

#-----------------------------------------------

def translate(text):
  translator=Translator(to_lang="hi")
  translation= translator.translate(text)
  print(translation)
  return translation



#------------------------------------------------

@client.tree.command(name="translate", description="Translated pdf summary and quiz")
@commands.cooldown(1,5,commands.BucketType.user)
async def score(content: discord.Interaction,book:discord.Attachment):
    await content.response.defer(ephemeral=True)
    if content.user.voice != None:
        print("celeb 1")
        vc = await content.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        print("celeb 2")
        vc.play(discord.FFmpegPCMAudio("intro.wav"),after=lambda e: asyncio.run_coroutine_threadsafe(summary(content,vc), client.loop))
        #---------------------------------
        buffer = io.BytesIO()
        await book.save(buffer)
        buffer.seek(0)
        reader = PyPDF2.PdfReader(buffer)
        #---------------------------------
        conversation = [{"role":"system", "content":"You are master tutor and all of your students get great grades because of you. Concise the text that is given to you and make it useful for the students. All important facts and details should remain. Also give 10 questions as a quiz. These should only have true or false as an answer. Mention the answer too. DO NOT LEAVE any important info. Make it below 500 characters."}]
        conversation.append({"role":"user","content":'Here is the text'+str(reader.pages[5].extract_text())+'make the summar and a 10 question mini quiz having true or false as the answer.'})
        GPTresponse = gptclient.chat.completions.create(
        model="gpt-4",
        messages=conversation)
        conversation.pop()
        stringfinal = GPTresponse.choices[0].message.content
        #---------------------------------
        translated=translate(stringfinal)
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=f"{translated}",)
        response.write_to_file("output.mp3")
        #---------------------------------
        myEmbed = discord.Embed(title="Bot", description="hi", color=0x00ff00)
        await content.followup.send(embed=myEmbed)



#------------------------------------------------

client.run(discordtoken)