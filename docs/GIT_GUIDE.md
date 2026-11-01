# Git guide for the team (no prior experience needed)

Idea: `main` is the shared, working version. Each person works on their **own branch** (a private copy of the work), then merges it into `main` through GitHub. If you only edit your own files, merging never conflicts.

## One-time setup (each laptop)
```
git clone https://github.com/adithyx-0/iws-rl.git
cd iws-rl
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python check_setup.py
git config user.name "Your Name"; git config user.email "you@example.com"
```
Teammates need to be added as collaborators (repo Settings -> Collaborators) to push. (Otherwise: fork and open PRs from the fork.)

## Every day
```
git switch main
git pull                      # get the latest shared work
git switch -c YOUR-BRANCH     # first time only: create your branch (use: core, docs-analysis, compute)
# later days: git switch YOUR-BRANCH && git merge main   (brings in latest main, usually no conflict)
```

## Save and share your work
```
git status                    # see what changed
git add path/to/your/files    # add only YOUR files (not `git add -A` if unsure)
git commit -m "short description of what you did"
git push -u origin YOUR-BRANCH     # first push; later just: git push
```
Then on GitHub: open the repo -> "Compare & pull request" -> create PR into `main`. The owner (Laptop A) clicks "Merge pull request". After merging, everybody does `git switch main && git pull`.

## Do not commit
`venv/` (huge), `__pycache__/`, secrets. They are already in `.gitignore`.

## If you get a conflict (rare)
It only happens if two people edited the same lines of a file. Git marks the file:
```
<<<<<<< HEAD
your version
=======
their version
>>>>>>> main
```
Open the file, keep the right text, delete the 3 marker lines, then:
```
git add THE_FILE
git commit -m "resolve conflict"
```
If unsure, stop and ask Laptop A rather than guessing. Never use `git push --force`.

## Useful safe commands
- `git log --oneline -10` last commits; `git diff` what changed; `git switch -` go back to the previous branch.
- Undo an uncommitted edit to one file: `git restore path/to/file`.
