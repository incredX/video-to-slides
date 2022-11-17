# Video to slides

This is a project idea to download screenshots of the slides from video recordings.

Initially it will be very specific to a course in our university.

# Contribution

In this project after the first commit, every change will be handled within an issue assigned to contributor.


## Dependencies

- use  ``` pip install -r requirements.txt ``` or  ``` pip3 install -r requirements.txt ``` in the terminal, to install all the dependencies.

### PyTesseract
- install using Homebrew ```brew install tesseract```
- copy installation path inside [config.yml](./config/config.yml) under `TESSERACT_PATH`, to find the path use ```which tesseract```