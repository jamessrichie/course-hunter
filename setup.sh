# Run in course-hunter root directory
pip3 install -r requirements.txt
git update-index --skip-worktree config/credentials.json
git update-index --skip-worktree config/joint-registration.json

osascript setup-safari.scpt