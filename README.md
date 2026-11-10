# Surprise Site 🎉

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Add or edit content
- **Team messages:** edit `messages.json` (one `{ "name": ..., "message": ... }` entry per person).
- **Title, intro, closing, photo:** edit `config.json`. For a photo, put the image in this folder
  (e.g. `team.jpg`) and set `"photo": "team.jpg"`.

## Deploy via git (Streamlit Community Cloud)
```bash
git init
git add .
git commit -m "Surprise site"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
Then go to https://share.streamlit.io, click **Create app**, pick the repo, branch `main`, and main file `app.py`.
Every later `git push` updates the live site. Use a **private repo** if you don't want the messages public
(Community Cloud supports private repos); the app URL itself is only known to whoever you share it with.
