import sys 

'''
ignore __pycache__
add path to repo
'''
sys.dont_write_bytecode = True

import os
import warnings
warnings.filterwarnings('ignore')

import git
from github import Github, InputGitTreeElement
import base64

repo = git.Repo('.', search_parent_directories=True)
# path = repo.working_tree_dir
os.chdir(repo.working_tree_dir)
# sys.path.append(path)

import SMARTControl as sc
database_fn = 'Data/database.db'
Get = sc.queries.Get(database_fn)
dt = sc.utils.HydraulicGradient (Get, size = 1)    




'''
Commit locally
'''

    
# repo_dir = 'PirnaCaseStudy'
# repo = git.Repo(os.getcwd())


# file_name = 'Vectors.csv'
# file_path = [f'Data/PostProcessed/{file_name}']



# dt = str(datetime.now()).\
#     replace(':','-').\
#         replace(' ','_')
# commit_message = f'Test_Database_LastUpdated-{dt}'


# repo.index.add(file_path)
# repo.git.commit( '-m', commit_message)



# '''
# Add to Github
# '''
# with open('D:\Repos\AccessToken.txt', 'r') as f:
#     token = f.readline()

# g = Github(token)    
# repo = g.get_user().get_repo('PirnaStudyCase')
# master_ref = repo.get_git_ref('heads/master')
# master_sha = master_ref.object.sha
# base_tree = repo.get_git_tree(master_sha)
# element_list = list()

# with open(file_path) as input_file:
#     data = input_file.read()
#     if file_path.endswith('.png'): # images must be encoded
#         data = base64.b64encode(data)
       
# element = InputGitTreeElement(file_path, '100644', 'blob', data)
# element_list.append(element)

# tree = repo.create_git_tree(element_list, base_tree)
# parent = repo.get_git_commit(master_sha)
# commit = repo.create_git_commit(commit_message, tree, [parent])
# master_ref.edit(commit.sha)
