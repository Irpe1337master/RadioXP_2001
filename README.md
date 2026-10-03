# Friend Radio

A clock-synced AI music radio in a Windows Media Player look. Works on GitHub Pages.

## Set up
1. Put MP3s in `music/<genre>/` (folder name = genre, e.g. `music/skyrim/`).
2. Run `pip install mutagen` once, then `python3 scan_music.py`. It rebuilds `tracks.json` with titles, artists and exact durations.
   - Name files `Artist - Title.mp3` or add ID3 tags to get credits.
3. Push to GitHub, then Settings > Pages > deploy from branch.
4. Test locally with `py serve.py` (Windows) or `python3 serve.py`, then open http://localhost:8000. Don't use `http.server`: it can't seek in audio, so sync breaks.

The password is `mellon`. When the page says "Speak, friend, and enter", type it.

## Invite links
Pick a genre, click **Copy invite link**, and send it. Friends unlock the page, land on the same genre, press Play if needed, and hear the same moment. The link has no password in it.

## Change the password
`printf 'newpassword' | sha256sum`, then paste the result into `PASS_HASH` near the top of the script in `index.html`.
This only keeps casual visitors out. The files are still public.

## How the sync works
All stations loop forever from a fixed start date (`EPOCH`). The page uses the current time to work out which track is playing and how far in.
- Adding, removing or renaming tracks changes the schedule, so stations jump for everyone. Prefix filenames with numbers (`01 - ...`) to control order.
- Friends' device clocks must be roughly correct (automatic time on).
- Audio on another domain needs CORS enabled for the visualizer.