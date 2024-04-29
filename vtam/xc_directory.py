import os

def open_dir(directory,new_directory,force):
    '''
    Open a directory and get its parameter, and create the output directory if neccesary

    Param:
    :param directory: path from the directory
    :type directory: str \n
    :param new_directory: path from the output directory
    :type new_directory: str\n
    Return:
    :return task_list: dictionnary of each couple of each path from template file, output file
    :type task_list: dict\n
    :return marker_verif_file: path from file needed for consistency checking or None if not in the directory
    :type marker_verif_file: str\n
    :return var_file: path from the file containing the variant or None if not in the directory
    :type var_file: str\n
    
    In out:
    :in out force: force or not file generation
    :type force: boolean
    '''
    file_dict,marker_verif_file,var_file,force = open_param(directory,force)
    if not os.path.isdir(new_directory):
        os.mkdir(new_directory)
    task_list = {}
    for file_path in [file.split(os.sep)[-1] for file in file_dict] :
        new_path = new_directory + os.sep + file_path
        task_list[directory+ os.sep + file_path] = new_path
    
    return task_list,marker_verif_file,var_file,force

def open_param(directory:str,force) :
    '''
    Get the parameter from a directory (list of files, variant and consistency)
    
    Param:
    :param directory: path from the directory
    :type directory: str \n

    Return:
    :return new_flist: dictionnary of each couple of each path from template file, output file
    :type new_flist: dict\n
    :return marker_verif_file: path from file needed for consistency checking or None if not in the directory
    :type marker_verif_file: str\n
    :return var_file: path from the file containing the variant or None if not in the directory
    :type var_file: str\n
    
    In out:
    :in out force: force or not file generation
    :type force: boolean
    '''
    #Get the list of the content from the file
    flist = os.listdir(directory)
    marker = False
    liste = False
    force = force
    marker_file = None
    var_file = None
    new_flist =[]
    for f in flist :
        extension = f.split('.')[-1]
        if extension == 'var':
            var_file = directory + os.sep + f
        elif extension == 'marker':
            marker_file = [directory + os.sep + f]
            marker = True
        elif extension == 'list':
            new_flist = open_list(directory,f)
            liste = True
    if not liste :
        return find_files(directory)
    if not marker :
        force = True
    return new_flist,marker_file,var_file,force


def find_files(directory:str):
    '''
    Find the templates in the directory

    :param directory: path from the directory
    :type directory: str\n
    :return file_dict: dictionnary of each couple of each path from template file, output file
    :type new_flist: dict\n
    '''
    flist = os.listdir(directory)
    majoritaire = {}
    for f in flist:
        extension = f.split('.')[-1]
        if extension not in ['var','marker','list'] :
            if extension in majoritaire.keys():
                majoritaire[extension] += 1
            else:
               majoritaire[extension] = 1
    
    max = 0 
    extension = ''
    for ext in majoritaire.keys():
        if majoritaire[ext] > max :
            max = majoritaire[ext]
            extension = ext
    
    file_dict = []
    for f in flist:
        ext = f.split('.')[-1]
        if ext == extension :
            file_path = os.path.join(directory,f)
            file_dict.append(file_path)
            sep=os.sep
            print(f'{f.split(sep)[-1]} oppened\n')

    return file_dict


def open_list(directory : str,file_ :str) -> list:
    '''
    Open the list file and get the list.

    :param directory: path from the directory
    :type directory: str\n
    :param file_: name from the list file
    :type file_: str\n

    :return file_dict: dictionnary of each couple of each path from template file, output file
    :type new_flist: dict\n
    '''
    with open(os.sep.join([directory,file_]), 'r') as file:
        file_dict = []
        for line in file:
            line = line.strip().split()
            for vfile in line:
                file_path = os.path.join(directory,vfile)
                if os.path.isfile(file_path):
                    if not file_path in file_dict :
                        file_dict.append(file_path)
                        sep=os.sep
                        print(f'{vfile.split(sep)[-1]} oppened\n')
                else:
                    print(f'WARNING : {vfile} is listed but is not a file or does not exist\n')
        return file_dict

def result_file(dirpath,args): 
    '''
    Create the result file in order to keep track of the used markers
    
    :param dirpath: path from the output file
    :type dirpath: str\n
    :param args: state from each used markers
    :type args: dict
    '''   
    with open(os.path.join(dirpath,'result.txt'),'w') as result :
        txt = 'MARQUEURS UTILISES\n'
        for marker,state in args.items() :
            if state:
                txt += '\t+'+marker+'\n'
            else :
                txt += '\t-'+marker+'\n'
        result.write(txt)