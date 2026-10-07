# Missile Command Repair Lab - Lab 4

The updated application is `Lab-4/game.py`. The original root `game.py` is preserved for the before recording. All four tasks are implemented. Application commits are local; they have not been pushed to GitHub.

## Setup and run

Use Python 3.10 or newer. From the repository root on macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pygame
python3 Lab-4/game.py
```

Run the original before version separately:

```bash
python3 game.py
```

## Controls

- Left-click at least 20 pixels above the ground to fire at the clicked point.
- R resets the game, ammunition, score, wave, repair bookkeeping, and city messages.
- Close the window to quit.

## Implemented tasks

| Task | Behavior | Separate commit |
| --- | --- | --- |
| 1 | Select the nearest alive battery with ammo greater than zero; safely skip launch if none exist; spend one ammo per successful launch. | `aca9367` |
| 2 | Clamp progress to 0-1; smoothly blend integer RGB from white through yellow and orange to red. | `422c9c6` |
| 3 | Show CITY DESTROYED! near a newly destroyed city for two seconds. Repeat hits and battery hits do not retrigger it. It remains visible during game-over and resets with R. | `516b72e` |
| 4 | Return 2000 for the repair threshold and use repairs_awarded to restore one destroyed city at each new milestone. Game-over prevents repairs. | `f549159` |

Additional review fix commit `2c901de` prevents interceptor overshoot/early detonation and processes every repair milestone when a score update crosses several. Production scoring, missile impacts, explosion lifetime/radius, and collision rules remain unchanged.

## Verification

```bash
python3 Lab-4/tests/test_game.py
```

Actual result: 24 tests passed. The environment had no Pygame and could not install it, so the run used the test-only vector double and drawing spies. These checks are not a graphical playthrough or video evidence. If Pygame is installed, the same script uses real Pygame vectors with a dummy SDL driver; drawing assertions still use spies.

The test script is separate from normal gameplay. It seeds randomness and sets up scores/destruction only inside tests. The application does not import it or contain demonstration cheats.

See `EVIDENCE.md`, `EVIDENCE.pdf`, and the raw logs in `evidence/`. `PROMPTS.md` preserves the three user prompts from this conversation, but is not a replacement for the complete chat history.

To rebuild the PDF after editing the evidence or prompt files:

```bash
python3 -m pip install reportlab
python3 Lab-4/tools/build_report.py
```

## Submission links - fill these yourself

| Required item | Status / placeholder |
| --- | --- |
| Individual repository URL | `[MISSING: YOUR_INDIVIDUAL_REPOSITORY_URL]` |
| Before-video URL | `[MISSING: YOUR_BEFORE_VIDEO_URL]` |
| After-video URL | `[MISSING: YOUR_AFTER_VIDEO_URL]` |
| Complete chat-history URL | `[MISSING: YOUR_CHAT_HISTORY_URL]` |
| Genuine gameplay screenshots | `[MISSING: capture from the real Pygame window]` |
| Student name / SRN / section | `[MISSING: verify and fill your submission details]` |

The current origin points to the supplied course repository, not a confirmed individual submission repository. Create or confirm your own repository and replace the placeholder before pushing:

```bash
git remote set-url origin "YOUR_INDIVIDUAL_REPOSITORY_URL"
git push -u origin main
```

Do not paste the placeholder literally. Replace it with the actual URL of your individual repository. If the destination already has unrelated commits, inspect that history first; do not force-push.

If you downloaded `MissileCommand_Lab4.bundle` from this chat to Downloads, it includes the application, documentation, and complete Git commit history:

```bash
git clone ~/Downloads/MissileCommand_Lab4.bundle MissileCommand-Lab4
cd MissileCommand-Lab4
```

Then run the setup commands above and set origin to your individual repository URL.

## Genuine 10-second recording plans

Before video: run root game.py. Before starting the recording, use the left battery's 10 shots while the other batteries retain ammo. Record approximately 3 seconds showing the left battery at 0 ammo, 4 seconds clicking above it and observing no launch, and 3 seconds showing another battery still has ammo. Rehearse before recording so missile impacts do not obscure the bug.

After video: run Lab-4/game.py. Play normally before starting the 10-second capture. Deplete one battery, keep another battery available, let at least one city be destroyed, then approach a 2000-point milestone through normal play. Keep recording a longer real session until a useful continuous 10-second interval exists. A practical target is: seconds 0-3 click above the empty battery to show fallback and one ammo consumed; seconds 3-5 show an explosion shifting colors; seconds 5-7 allow a missile hit to show CITY DESTROYED!; seconds 7-10 cross the next milestone and show a destroyed city rebuilt. Exact event timing is not guaranteed. If all features do not fit, record supplemental real clips instead of forcing scores or presenting test states as gameplay. Never splice separate events and call them one continuous interval.

On macOS, Shift-Command-5 opens screen-recording controls. Select the game window area and start recording. Record ahead of the desired events, then trim one continuous interval to 10 seconds. Save as before.mp4 and after.mp4 and upload them to a location accepted by your course. Check video duration and viewing permissions.

## Preserve the complete chat

Use this conversation's Share option if available. Create or refresh its shared link after the final response so all three prompts, assistant explanations, and available tool activity are preserved. Open the URL in a private window to confirm what the recipient can view. If sharing omits tool activity, also save/export or print the complete conversation and retain the raw verification logs. The prompt appendix alone is not complete chat history. Confirm the course accepts the chosen history format and set its viewing permissions.

## Manual completion checklist

- [ ] Verify student name, SRN, and section; do not infer them from memory.
- [ ] Import/download the repository with its Git history; run the real game with Pygame.
- [ ] Record genuine 10-second before and after videos; add supplemental clips if needed.
- [ ] Capture genuine screenshots if desired and label their source/version.
- [ ] Fill the four URL placeholders and verify recipient access.
- [ ] Preserve/share the full conversation, including the final results.
- [ ] Push main to your individual repository and inspect its Lab-4 folder and separate commits online.
- [ ] Submit the items requested by the professor's email/portal. The supplied root README explicitly asks for the two videos and the complete chat link; repository/documentation requirements also come from your instruction about the email.
