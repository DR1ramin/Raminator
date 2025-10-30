from google import genai

client = genai.Client(api_key="AIzaSyCVI_2GQSVSr4mJUkmObt38Xp53Q8RJS88")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Based on this text'This guide explains how to connect your digital wallet and transfer the tokens you've earned. It's like connecting your bank account to a platform to move your money!', write a prompt for creating an image using AI, and mark the beginning and end of the prompt with the '*' character,prompt limit to 200 character.",
)

print(response.text)