# Repository Guidelines

## Project Structure & Module Organization
Core runtime lives in `src/assistive_vision/`, where `system.py` orchestrates detection, tracking, distance checking, navigation, and voice output modules. Shared configuration stays in `src/assistive_vision/config.py`; adjust Raspberry Pi, YOLO, or audio parameters there before committing. Runtime artefacts belong under `models/` (weights), `data/` (fixtures, captures), and `logs/` (diagnostics). Developer documentation now sits in `docs/`, while automation utilities reside in `scripts/`. Keep new integration or smoke tests beside the existing suites inside `tests/` following the `test_<feature>.py` convention.

## Build, Test, and Development Commands
Create a virtual environment with `python -m venv venv` then activate it (`source venv/bin/activate` or `.\venv\Scripts\activate`). Install dependencies using `pip install -r requirements.txt`. Run the full pipeline from the project root with `PYTHONPATH=src python -m assistive_vision` (PowerShell: `$env:PYTHONPATH="src"; python -m assistive_vision`). Use `python scripts/run_system.py --no-display` when you need headless Raspberry Pi runs, adding `--debug` for verbose logs. Execute regression tests with `PYTHONPATH=src pytest` and trigger the continuous audio smoke test via `PYTHONPATH=src python tests/test_continuous_alerts.py`. Refresh YOLO assets by downloading weights into `models/` (`wget ... -P models/`) or running `python -c "from ultralytics import YOLO; YOLO('models/yolov8n.pt')"`.

## Coding Style & Naming Conventions
Follow PEP 8: four-space indentation, `snake_case` functions, and `PascalCase` classes (`VoiceAlert`, `DisabilityAssistanceSystem`). Keep constants in `UPPER_SNAKE_CASE` and bilingual strings centralized in configuration helpers. Favour small, single-purpose functions with docstrings describing device-specific behaviour. Run `python -m black src/assistive_vision/system.py src/assistive_vision/object_detector.py src/assistive_vision/voice_alert.py` before opening a PR to maintain consistent formatting.

## Testing Guidelines
Focus on alert cadence, distance thresholds, and tracker stability. Structure pytest suites as pure functions and keep manual printouts confined to ad-hoc scripts. Use `PYTHONPATH=src pytest` for the full suite, then re-run `PYTHONPATH=src python tests/test_continuous_alerts.py` when adjusting TTS cadence; attach any anomalous `logs/summary_*.txt` artefacts to review notes. Keep fixture media under 5 MB inside `data/fixtures` to avoid bloating the repository.

## Commit & Pull Request Guidelines
Write imperative, scoped commit messages—Conventional Commits (`feat: improve close-range prompts`) are encouraged. Group code, assets, and docs per change set so reviewers can reproduce quickly. Pull requests should outline the change, list validation steps (include Raspberry Pi model and commands run), provide before/after screenshots or audio snippets when relevant, and cross-reference roadmap entries stored in `docs/PROJECT_ROADMAP.md`. Request review from maintainers of modules you touched and wait for at least one approval before merging.
