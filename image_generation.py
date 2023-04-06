import openai
import requests
import json
from PIL import Image
from io import BytesIO
import prompt_generation
#pip3 install Pillow
# pip3 install openai  

          
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
openai.api_key = open_file('api_key.txt')


def generate_image(prompt_image, output_image_path):
    # Configurer les paramètres de la requête à l'API DALL-E
    query = {
        "model": "image-alpha-001",
        "prompt": prompt_image,
        "num_images": 1,
        "size": "512x512",
        "response_format": "url"
    }
    response = openai.Image.create(**query)

    # Récupérer l'URL de l'image générée
    image_url = response["data"][0]["url"]

    image_data = requests.get(image_url).content
    with open(output_image_path, "wb") as f:
        f.write(image_data)

    # Afficher l'image avec la bibliothèque Pillow (PIL)
    image = Image.open(BytesIO(image_data))
    image.show()

if __name__ == "__main__":

    prompt_image = f'creer une image réaliste sur : {prompt_generation.generated_text}'
    output_image_path = f"image-thumbails/{prompt_generation.titre}.png"
    generate_image(prompt_image, output_image_path)


