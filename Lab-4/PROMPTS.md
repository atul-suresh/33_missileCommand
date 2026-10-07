# Exact user prompts from this conversation

The three blocks below preserve the three user implementation prompts verbatim, including the literal backslash in Prompt 3. These are user prompts only. Preserve the complete chat separately, including assistant responses and available tool activity. No complete chat-history URL has been provided.

## Prompt 1

```text
Work directly in this repository to complete my Missile Command Repair Lab. Implement changes, rather than only explaining them.

Read README.md, game.py, and any applicable repository instructions. The submission email requires the updated application under Lab-4 and a separate Git commit for each of the four tasks.

Create Lab-4/game.py from the original game.py. Preserve the original root game.py so I retain the before version. Make all application changes in Lab-4/game.py.

Complete Task 1:

- nearest_battery(target) must consider only batteries that are alive and have ammo greater than zero.
- Return the nearest eligible battery.
- Return None if no eligible batteries exist.
- Update launch() to handle None without crashing or consuming ammunition.
- Preserve the existing targeting and gameplay rules.

Verify selection when the closest battery is depleted, destroyed, available, and when every battery is unavailable. Check that a successful launch consumes exactly one ammunition unit.

Create a separate commit for Task 1. Do not implement Tasks 2–4 yet. If Git commits are blocked by missing author configuration, report that and provide the exact commands without inventing my identity.

Finish with a concise explanation of the change, actual verification results, the commit hash if created, and the terminal command to run Lab-4/game.py.
```

## Prompt 2

```text
Continue working in Lab-4/game.py and preserve the verified Task 1 fix.
Complete Task 2:
Implement explosion_color(progress) with a smooth transition from white-hot through yellow/orange to red as the explosion ages. Clamp progress to 0–1 and return integer RGB components between 0 and 255. Preserve explosion timing, radius, and collision behaviour. Verify the start, midpoint, end, and out-of-range inputs. Create a separate Task 2 commit before beginning Task 3.
Complete Task 3:
Implement on_city_destroyed(city) so destroying a previously standing city produces visible, temporary feedback in the game, such as “CITY DESTROYED!” near that city. Use the existing callback signature and a simple timer-based approach. Avoid external assets and unnecessary global state. Ensure the feedback is triggered only for a newly destroyed city, expires correctly, and resets when R restarts the game. Make sure the feedback is still visible if the destroyed city was the last surviving city.
Verify that hitting an already destroyed city or hitting a battery does not trigger city-destruction feedback. Create a separate Task 3 commit.
Keep the implementation small and readable. Do not implement Task 4 yet. Finish with actual verification results, commit hashes if created, and instructions for observing both features.
```

## Prompt 3

```text
Complete the remaining work without requiring another AI prompt.

Complete Task 4 in Lab-4/game.py:

- Implement city_repair_threshold() to return 2000.
- Use the existing repairs_awarded bookkeeping.
- Verify that reaching each new 2000-point milestone restores one destroyed city when one is available.
- Verify that the same milestone does not repeatedly restore cities, that having no destroyed cities causes no error, and that R resets the repair bookkeeping.
- Preserve game-over behaviour.\
  Create a separate Task 4 commit.

Review and verify all four tasks together. Check launching, ammunition use, interceptor arrival, explosion collisions, missile impacts, wave progression, city repair, game over, and reset. If you discover a reproducible issue affecting the README’s expected behaviour, make a minimal fix, explain it, and put it in an additional separate commit.

Use deterministic checks where possible. Any helper that forces scores or destruction for testing must be separate from normal gameplay. Do not add fake gameplay evidence or alter production scoring to make the demonstration easier.

Prepare submission documentation under Lab-4:

- README with setup, controls, and all four implemented tasks.
- An evidence report containing the changes, actual test results, commit information, and genuine screenshots if the environment supports capturing them.
- Generate a PDF version if supported. Clearly mark any missing user-provided information.
- Include the three exact prompts from this conversation if available, and explain how I should preserve the complete chat history.
- Provide labelled placeholders for my individual repository URL, before-video URL, after-video URL, and chat-history URL. Do not invent links or claim missing evidence is complete.

Commit documentation separately. Finish with the exact run and Git push commands, a practical 10-second after-video recording plan, and a checklist of anything I must manually complete before submission.
```
