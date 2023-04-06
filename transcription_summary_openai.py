# import openai
import os
import re
import sys
import json
import openai
import random
import pathlib

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
openai.api_key = open_file('api_key.txt')

PATH_TO_FOLDER = sys.argv[-1]
CURR_DIR = pathlib.Path().resolve()
CHATGPT_SENTENCE_LIMIT = 15

# prompts that we will ask chatgpt
chatgpt_prompt = "Est-ce que tu peux me generer un titre , un résumé entre 60 et 70 mots, et une liste de 10 mot-clés d'après ce texte : "
chatgpt_prompt_format = "\nTitre:\n\Résumé:\n\Mot-clés: (séparé par des virgules)"
chatgpt_prompt_if_too_long = "Peux tu faire un résumé de 60 à 70 mots du texte suivant :\n"

#regex used to extract the necessary information from chatgpt last output about a podcast
titre_regex = r"(?:.|Titre:|Titre :) (.+?)(?:\nRésumé|Résumé|\.)"
resume_regex = r"(?:Résumé:|\nRésumé:|Résumé :|\.) (.+?)(?:[Mm]ot(s?)-clés|\n)"
motscles_regex = r"(?:\n[Mm]ot(s?)-clés:|[Mm]ot(s?)-clés:|[Mm]ot(s?)-clés :) (.+)"
OUTPUT_FILE = 'summary_results.json'


def handle_gpt_output(output, is_intermediate_summary=True):
    if is_intermediate_summary:
        return output
    else:
        titre = re.search(titre_regex, output)  # Split the response into lines
        resume = re.search(resume_regex, output)  # Split the response into lines
        motscles = re.search(motscles_regex, output)  # Split the response into lines

        if titre != None and resume != None and motscles != None:  # Ensure there are at least 4 lines in the response
            print(motscles.group(0))
            result = {
                "title": titre.group(1).strip(),  # Extract title from the 2nd line
                "summary": resume.group(1).strip(),  # Extract summary from the 4th line
                "keywords": motscles.group(4).strip() # Extract keywords from the 6th line
            }
            return result
        else:
            print("Unexpected response format")
            print(output)
            return None

def summary(text, asked_prompt, format_final_prompt=None):
    # Creates the prompt dependeing if it is the final request prompt or not
    prompt = f"{asked_prompt}{text}{format_final_prompt}" if format_final_prompt else f"{asked_prompt}{text}"

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=670,  # Increase the number of tokens
            n=1,
            stop=None,
            temperature=0.05,  # Decrease the temperature
        )

        return handle_gpt_output(response.choices[0].text.strip(), False if format_final_prompt else True)

    except Exception as e:
        print("Error while summarizing the text:", e)
        return None

def export_to_json(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

def main():
    # Samples a random file from all the txt transcription files
    files = random.sample(os.listdir(os.path.join(CURR_DIR, PATH_TO_FOLDER)), 10)

    print(files)
    files_gpt_output = []
    for file in files:
        split_file= []

        with open(f'{CURR_DIR}/{PATH_TO_FOLDER}/{file}', mode='r') as f:
            tmp_content = ''
            limit_threshold = CHATGPT_SENTENCE_LIMIT
            # The file is cut in pieces of CHATGPT_SENTENCE_LIMIT size so that the openai is able to process each bit of the file
            for line in f:
                if limit_threshold > 0:
                    tmp_content += line
                    limit_threshold -= 1
                else:
                    split_file.append(tmp_content)
                    limit_threshold = CHATGPT_SENTENCE_LIMIT
                    tmp_content = ''
            # in case where the sentence limit is never reached, happens at end of file mostly      
            split_file.append(tmp_content)
            f.close()

        # summarize the all text bits by bits
        file_summary = ""
        for item in split_file:
            file_summary += summary(item, chatgpt_prompt_if_too_long)
        
        #once the all file is summarized we asked chatgpt for title, overall summary and keywords
        print('final request', len(file_summary))
        files_gpt_output.append(summary(file_summary,chatgpt_prompt, format_final_prompt=chatgpt_prompt_format))
    
    # Once all the file summarization are done everything is saved in json format
    export_to_json(files_gpt_output, OUTPUT_FILE)

if __name__ == '__main__':
    main()

