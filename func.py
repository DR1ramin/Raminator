from google import genai

client = genai.Client()

myfile = client.files.upload(file='media/sample.mp3')

response = client.models.generate_content(
  model='gemini-2.0-flash',
  contents=['Describe this audio clip', myfile]
)

print(response.text)