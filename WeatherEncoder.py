import base64
import json
import mimetypes
import os
from re import S
import shutil
import openai
import exiftool
import logging
from pathlib import Path


class WeatherEncoder:
    def __init__(self, apiKey, model="gpt-4o"):
        self.Log = logging.getLogger("WeatherEncoder")
        self.BasePath = Path(__file__).resolve().parent
        self.CheckPath = os.path.join(self.BasePath, "assets","unprocessed")
        self.ProcessedPath = os.path.join(self.BasePath, "assets","backgrounds")
        self.Model = model
        self.ApiKey = apiKey
        self.Client = openai.OpenAI(api_key=apiKey)
        self.EnableTrace = os.getenv("ENABLE_TRACE", "No") == "Yes"
        

    def ProcessAllFiles(self):
        ImageFiles = [f for f in os.listdir(self.CheckPath)
                      if f.lower().endswith(('.jpg','.jpeg','.png'))]
        if (len(ImageFiles) == 0):
            self.Log.debug(F"ProcessAllFiles: No ImageFiles found")
            return

        allStates = ['Sunrise','Sunset','Night','Daylight']
        allConditions = ['Clear','PartlyCloudy','Cloudy','Overcast','Foggy','Lightning','LightRain','MediumRain','HeavyRain','Snow']

        allStatesItems = ""
        for state in allStates:
            allStatesItems += F" - {state}"
        allConditionsItems = ""
        for condition in allConditions:
            allConditionsItems += F" - {condition}"

        systemTag = "You are a photo tagging assistant. You are going to help define the two attributes that describe the image closest.";
        systemTag += "First, you will decide the timing tag, which MUST be ONLY one of the following:"
        systemTag += allStatesItems
        systemTag += "Secondly, you will decide the weather type tag, which has the following rules:"
        systemTag += " 1. If an image has Lightning, always pick 'Lightning'"
        systemTag += " 2. If an image has Fog but no Rain or Lightning, always pick 'Foggy'"
        systemTag += " 3. If an image has Rain, pick the one that is the most likely; if there's almost no visibility or its mostly dark, pick 'HeavyRain'. If there's a lot of visibility and light, pick 'LightRain.' If its somewhere in the middle, pick 'MediumRain.'"
        systemTag += " 4. You MUST ONLY pick ONE item from the following list."
        systemTag += " 5. You will be provided the file name of the image which can help determine the Timing and Weather Type. If it has a Weather Type in the file name, use that Weather Type instead (so if a File has 'Foggy' in the file name, use 'Foggy')"
        systemTag += allConditionsItems
        systemTag += "Your output must be only in the format: <Timing>,<WeatherType> (For example, 'Daylight,Clear') Do not provide any additional output, or justification."
        self.Log.info(F"ProcessAllFiles: Encoding {len(ImageFiles)}...")
        for image in ImageFiles:
            self.Log.info(F"ProcessAllFiles: Encoding {image}...")
            imagePath = os.path.join(self.CheckPath, image)
            with open(imagePath, "rb") as imageFile:
                Base64Image = base64.b64encode(imageFile.read()).decode("utf-8")
                mimeType = self.GetMimeType(imagePath)
                userMessages = [
                    {"type":"image_url", "image_url": {"url": f"data:{mimeType};base64,{Base64Image}"}},
                    {"type":"text", "text": F"Image File Name: {image} / What are the two tags for this image?"}
                ];
                messages = [
                    {"role":"system", "content": systemTag},
                    {"role":"user", "content": userMessages}
                ]
                
                isValidResponse = False
                Tags = None
                numberTries = 0
                while numberTries < 3 and not isValidResponse:
                    ChatGPTResponse = self.Client.chat.completions.create(model=self.Model,messages=messages,max_tokens=100)
                    numberTries += 1
                    rawReply = ChatGPTResponse.choices[0].message.content.strip()
                    self.Log.debug(F"ProcessAllFiles: ChatGPT said '{rawReply}'...")
                    Tags = [t.strip() for t in rawReply.split(',')]
                    messages.append({"role":"assistant", "content": rawReply})
                    responseMessage = ""
                    if (len(Tags) < 2):
                        responseMessage = F"You provided {len(Tags)} but you should only provide two comma-delimited tags."
                        self.Log.warn(F"WeatherEncoder: ChatGPT provided {len(Tags)}, which is incorrect.")
                    elif (not any (t in allStates for t in Tags)):
                        responseMessage = F"Neither of the tags you provided contained a valid Timing Tag. Remember, you MUST include one tag from the following list: " + allStatesItems
                        self.Log.warn(F"WeatherEncoder: ChatGPT didn't provide a Timing Tag.")
                    elif (not any (t in allConditions for t in Tags)):
                        responseMessage = F"Neither of the tags you provided contained a valid Weather Type Tag. Remember, you MUST include one tag from the following list: " + allConditionsItems
                        self.Log.warn(F"WeatherEncoder: ChatGPT didn't provide a Weather Type Tag.")
                    else:
                        isValidResponse = True
                        self.Log.info(F"WeatherEncoder: ChatGPT Success!")
                    if (not isValidResponse):
                        messages.append({"role":"user", "content": responseMessage})

            if (not isValidResponse):
                self.Log.warn(F"WeatherEncoder: ChatGPT just didn't work this time. Stopping.")
                continue

            if (self.EncodeImage(imagePath, Tags)):
                self.MoveToProcessed(imagePath);


    def GetMimeType(self, filePath):
        mimeType, _ = mimetypes.guess_type(filePath)
        return mimeType or "application/octet-stream"
                

    def EncodeImage(self, path, tags):
        tagString = "; ".join(tags)

        try:
            with exiftool.ExifTool() as et:
                et.execute(
                    f"-IPTC:Keywords={tagString}",
                    f"-XMP:Subject={tagString}",
                    "-overwrite_original",
                    path)

                output = et.execute("-XMP:Subject", "-json", path)
                metadata = json.loads(output)[0]
                readBack = metadata.get("XMP:Subject",[])

                expectedSet = set(tags)
                if isinstance(readBack, str):
                    readBackSet = set(k.strip() for k in readBack.split(';'))
                elif isinstance(readBack, list):
                    readBackSet = set(k.strip() for k in readBack)
                else:
                    readBackSet = set()

                if expectedSet == readBackSet:
                    return True

                self.Log.error(F"WeatherEncoder: Tag mismatch! Expected: {expectedSet}, Found {readBackSet}")
        except Exception as e:
            self.Log.error(F"WeatherEncoder: Failed to write tags to {path}.")

        return False

    def MoveToProcessed(self, imagePath):
        try:
            fileName = os.path.basename(imagePath)
            newPath = os.path.join(self.ProcessedPath, fileName)
            shutil.move(imagePath, newPath)
            self.Log.info(F"WeatherEncoder: Moved {fileName} to processed folder.")
            return True
        except Exception as e:
            self.Log.error(F"WeatherEncoder: Failed to move {imagePath} to processed folder.")
        return False
               
