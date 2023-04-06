import os
import sys
import json
import pathlib

PARENT_FOLDER_PATH = sys.argv[1]
TO_WRITE_DIR = sys.argv[2]
CURR_DIR = pathlib.Path().resolve()
CONTENT_LIMIT = 270

def dirs_in(path_to_parent):
    """
    Returns the list of directories inside of a directory
    """
    list_dirs = []
    for fname in os.listdir(path_to_parent):
        if os.path.isdir(os.path.join(path_to_parent,fname)):
             list_dirs.append(fname)
    return list_dirs

def create_dataframe_from_json(file_name):
    """
    Creates and returns a dataframe containing the content, speaker and start time 
    of each phrase from the json transcription
    """
    df_list = []
    with open(file_name, 'r') as file:
        for line in file:
            json_line = json.loads(line)
            df_element =  split_content(json_line['tsa_content'], json_line['tsa_speaker'][0])
            df_list.extend(df_element)
        file.close()

    return df_list


def write_line(speaker, content, file):
    """
    Write in a txt file a phrase said by one of the speaker
    """
    line_to_write = f"{speaker} : {content}\n"
    file.write(line_to_write)

def write_transcript(df, file_name):
    """
    Goes through the dataframe to write each sentence (order by start time) into a txt file
    The mode for the file opening changes based on the file existence
    """
    
    mode = 'x'
    # Checks if the file exists if yes then the functions just writes over what was in the file
    if os.path.isfile(file_name):
        mode = 'w'
    
    with open(file_name, mode=mode) as file:
        for line in df:
            write_line(line[0], line[1], file)
        file.close()

def handle_dir(path_to_folder, to_write_file_name):
    """
    This function takes a folder containing a transcription 
    and extract the transcription file to apply the transformation to txt format

    TODO: take care of the case where path_to_folder has many sub folders
    """
    # collects all files of folder located at path_to_folder
    file_names = [f for f in os.listdir(path_to_folder)]

    print('----------', file_names)
    if len(file_names) == 0:
        print('empty directory')
        return

    # for this condition, the functions checks if the collected object is a file because it could be a directory (specific to the transcription_json folder)
    elif len(file_names) == 1 and os.path.isfile(f'{CURR_DIR}/{path_to_folder}/{file_names[0]}'):
        df = create_dataframe_from_json(f'{path_to_folder}/{file_names[0]}')
        write_transcript(df, f'{TO_WRITE_DIR}/{to_write_file_name}_{os.path.splitext(file_names[0])[0]}.txt')

    # this case is when the path_to_folder as many transcription files, it gathers them all inside the same dataframe
    elif len(file_names) > 1:
        df = []
        for file_name in file_names:
            df_file = create_dataframe_from_json(f'{path_to_folder}/{file_name}')
            df += df_file
        write_transcript(df, f'{TO_WRITE_DIR}/{to_write_file_name}_{os.path.splitext(file_names[0])[0]}.txt')
    
    # this case takes care of path_to_folder having a sub directory containing a transcription file (might be more but not in our case)
    elif len(file_names) == 1 and os.path.isdir(f'{CURR_DIR}/{path_to_folder}/{file_names[0]}'):
        handle_dir(f'{path_to_folder}/{file_names[0]}', f'{to_write_file_name}_{file_names[0]}')

def split_content(content,speaker):
    n = len(content)

    if n < CONTENT_LIMIT:
        return [[speaker, content]]
    
    cut_points = n//CONTENT_LIMIT
    split_content_list = []

    for _ in range(0,cut_points):
        period_before = content.rfind('.', 0, CONTENT_LIMIT)

        if period_before == -1:
            # If there is no period before the midpoint, find the nearest period after the midpoint
            period_after = content.find('.', CONTENT_LIMIT)

            if period_after == -1:
                # If there is no period after the midpoint, split the text at the midpoint
                 split_content_list.append([speaker, content[:CONTENT_LIMIT]])
                 content = content[CONTENT_LIMIT:]
            
            split_content_list.append([speaker, content[:period_after+1]])
            content = content[period_after+1:]

        split_content_list.append([speaker, content[:period_before+1]]) 
        content = content[period_before+1:]
    return split_content_list

def main():
    # If writing folder does not exist , we create it 
    if not os.path.exists(TO_WRITE_DIR):
        os.makedirs(TO_WRITE_DIR)
    
    for (dir_path, dir_names, file_names) in os.walk(PARENT_FOLDER_PATH):
        
        # For each dir we check if it contains sub directories then we apply the transformation function accordingly
        for dir_name in dir_names:
            print(dir_name)
            path_to_dir = f'{dir_path}/{dir_name}'
            sub_dir = dirs_in(path_to_dir)
            if  len(sub_dir) == 0:
                print('no sub folder')
                handle_dir(path_to_dir, f'{dir_name}')
            else:
                for folder in sub_dir:
                    print(folder)
                    handle_dir(f'{path_to_dir}/{folder}', f'{dir_name}_{folder}')
        # then for each file we apply the transformation from json to txt
        for file_name in file_names:
            print('file', file_name)
            df = create_dataframe_from_json(f'{dir_path}/{file_name}')
            write_transcript(df, f'{TO_WRITE_DIR}/{os.path.splitext(file_name)[0]}.txt')

if __name__ == "__main__":
    main()