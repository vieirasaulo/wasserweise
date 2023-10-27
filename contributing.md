# Contibuting 101 for the study project

### Workflow for project development/maintenance
1. Create an inssue on GitHub.
   - For a real project, link this issue to a project board
   - Create a new branch through git issue to solve that issue locally

2. Update your forked repository (see Workflow to update your forked version)
    - double check if the branch create is available (```git branch```)
    - Change your current branch to the issue branch ```git checkout <branch issue name>```
    - Make sure **you are not check out to the default branch (main or master)**
    - Fix the bug, add new functionalities and test your code.
    - Add in your commit message a [keyword](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests) to control the issue.
      - For instance: ```git commit -m "This fixes issue #1" -m "interpolation bug fixed"```
    - Push the code to GitHub using the new branch
      - ```git push origin <branch issue name>```
    - [Create a pull request](https://www.youtube.com/watch?v=x24fOAPclL4)



### Workflow to update your forked version
   - Fetch changes in the upstream repo to your forked repo
     - make sure upstream url is set (```git remote -v```)
     - ```git fetch upstream```
     - Merge the changes into your local fork. [Tutorial](https://www.youtube.com/watch?v=deEYHVpE1c8).
