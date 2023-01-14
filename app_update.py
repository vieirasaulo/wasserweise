'''
Module where the update function is written
'''

import sys 

'''
ignore __pycache__
add path to repo
'''
sys.dont_write_bytecode = True
import SMARTControl

'''
App to update the database and store it and commit to git and github        
'''
        
if __name__ == '__main__':
    SMARTControl.update.app_update(False , True)