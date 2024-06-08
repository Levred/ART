import os

def open_dir(directory, new_directory, force):
    """
    Opens a directory and retrieves necessary parameters.
    Creates the output directory if it doesn't exist and generates a task list for file processing.

    Args:
        directory (str): Path to the input directory.
        new_directory (str): Path to the output directory.
        force (bool): Flag to force file generation, bypassing some checks.

    Returns:
        tuple: Contains task_list (dict), marker_verif_file (str or None), var_file (str or None), and force (bool).
    """
    file_dict, marker_verif_file, var_file, force = open_param(directory, force)
    os.makedirs(new_directory, exist_ok=True)
    task_list = {os.path.join(directory, file_path): os.path.join(new_directory, os.path.basename(file_path)) for file_path in file_dict}

    return task_list, marker_verif_file, var_file, force

def open_param(directory: str, force):
    """
    Retrieves parameters from a directory, including marker and variant files.

    Args:
        directory (str): Path to the directory.
        force (bool): Flag to force file generation.

    Returns:
        tuple: Contains file list (list), marker_verif_file (str or None), var_file (str or None), and force (bool).
    """
    flist = os.listdir(directory)
    marker_file, var_file = None, None
    new_flist = []

    for f in flist:
        ext = f.split('.')[-1]
        if ext == 'var':
            var_file = os.path.join(directory, f)
        elif ext == 'marker':
            marker_file = [os.path.join(directory, f)]
        elif ext == 'list':
            new_flist = open_list(directory, f)

    if not new_flist:
        new_flist = find_files(directory)

    if not marker_file:
        force = True
    return new_flist, marker_file, var_file, force

def find_files(directory: str):
    """
    Finds and returns the list of files with the most common extension in the directory.

    Args:
        directory (str): Path to the directory.

    Returns:
        list: List of file paths.
    """
    flist = os.listdir(directory)
    majoritaire = {}

    # Count occurrences of each file extension
    for f in flist:
        ext = f.split('.')[-1]
        if ext not in ['var', 'marker', 'list']:
            majoritaire[ext] = majoritaire.get(ext, 0) + 1

    # Find the most common extension
    extension = max(majoritaire, key=majoritaire.get, default='')

    # Return list of files with the most common extension
    return [os.path.join(directory, f) for f in flist if f.endswith(extension)]


def result_file(dirpath, args): 
    """
    Crée le fichier de résultat pour suivre les marqueurs utilisés.

    Args:
    :param dirpath: Chemin du répertoire de sortie
    :type dirpath: str
    :param args: État de chaque marqueur utilisé
    :type args: dict
    """   
    with open(os.path.join(dirpath, 'result.txt'), 'w') as result:
        txt = 'MARQUEURS UTILISÉS\n'
        for marker, state in args.items():
            if state:
                txt += '\t+' + marker + '\n'
            else:
                txt += '\t-' + marker + '\n'
        result.write(txt)
