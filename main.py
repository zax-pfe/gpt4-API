import openai

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
openai.api_key = open_file('api_key.txt')

completion = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[{"role": "system", "content": "the answer must be less than 100 words"},
            {"role": "system", "content": "the user is someone named The Great Max, the system must speak to it like to a king"},
      {"role": "user", "content": "Tell me how to cook pasta "}]
)

print(completion)