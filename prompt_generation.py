import openai
import json

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
openai.api_key = open_file('api_key.txt')


# Chargez votre JSON avec titre, résumé et mots clés
json_file_path = "summary_results.json"
with open(json_file_path, "r") as file:
    json_data = json.load(file)
for file in json_data :
    titre = file["title"]
    résumé = file["summary"]
    mot_clés = file["keywords"]
# Créez un prompt pour GPT-3 en utilisant le titre, le résumé et les mots clés
    prompt = f"Créer un prompt détaillé et court pour generer une image adequat sur le sujet suivant: '{titre}'. Résumé: '{résumé}'. Mots clés: {mot_clés}."

    # Envoyez la requête à l'API GPT-3
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        n=3,
        stop=None,
        temperature=0.05,
    )

    # Affichez la réponse générée
    generated_text = response.choices[0].text.strip()
    print(response.choices[0])
print(f"{generated_text}")
