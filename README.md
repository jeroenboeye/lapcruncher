# Lapcruncher

Tooling to analyze per lap performance on crit races. Can also be used to look into regular rides.
The analysis uses gpx files of bike rides exported from Strava and (only?) works for this specific setup:
- Wahoo (ELEMNT)
- hr monitor
- power meter

## Lockfile update

The various tools result in slighlty different headers for the lockfile, but generate the same dependency lists.

### Rye

Adding a dependency:

```
rye add attrs
```

Lockfile is automatically updated and virtual environment is synced.

Adding a dev dependency:

```
rye add rich --dev
```

Dev lockfile is automatically updated and virtual environment is synced.

### Uv

Manually add a dependency in the pyproject.toml file.

```
uv pip compile -o requirements.lock pyproject.toml
```

### pip-compile

Manually add a dependency in the pyproject.toml file.

```
pip-compile --no-emit-trusted-host --no-emit-index-url -o requirements.lock pyproject.toml
```
