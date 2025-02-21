from openai import OpenAI

# API configuration
api_key = 'Replace_with_you_API_key'

base_url = "https://chat-ai.academiccloud.de/v1"

model = "meta-llama-3.1-8b-instruct"

# Start OpenAI client
client = OpenAI(
    api_key = api_key,
    base_url = base_url
)


# Get response
chat_completion = client.chat.completions.create(
        messages=[
 {"role":"system",
                   "content":"You are a helpful assistant"},
 {"role":"user",
  "content":"How tall is the Eiffel tower?"}
       ],
        model= model,
    )

# Print full response as JSON
print(json_dumps(chat_completion))
