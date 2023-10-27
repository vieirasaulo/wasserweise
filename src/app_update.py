# App to update the database, store it and commit to git and github
import wasserweise


if __name__ == "__main__":
    wasserweise.update.app_update(git_commit=True, github_push=True)
