import openai

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
openai.api_key = open_file('api_key.txt')

completion = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[{"role": "system", "content": "the answer must be less than 50 words "},
      {"role": "user", "content": "Tell me how to cook pasta "}]
)

print(completion)