# GripHook
A utility for mining and analyzing GitHub repositories

## Usage
- Step 1: Download pull request metadata from a repo
```sh
python -m lib.data --download-meta --repository achyudh/griphook --pages 10
```
- Step 2: Download the files modified in these pull requests
```sh
python -m lib.data --download-files --repository achyudh/griphook
```
