## Getting set up to run this program on a Windows computer

This program runs in a terminal (command prompt) window. To open a command prompt, search for "Command Prompt App"
in the Windows Search Box and open the app. You will need to set up a few things before you can get started. 

### Installing Python 3

This program is written in Python 3. At the command prompt enter "python" to see if Python is installed. If it is, you
should see the a Python version number- be sure the version is 3 or greater. That version number is followed by an
interactive Python session, otherwise known as a read-eval-print loop (REPL), where you can test out Python commands.
You should see the characters ">>>" when you start a REPL. Type "exit()" to quit.

If Python is not installed the Microsoft Store will open. Follow the prompts to install Python 3.

### Installing git 

At the command prompt, enter "git" to see if git is installed. If it is, you'll see a usage message with a list of git
subcommands. If not you'll get a message like "git is not recognized as an internal or external command, operable
program or batch file."

To install git:

1. Go to [https://git-scm.com/download/win](https://git-scm.com/download/win).
2. Click the "Download the latest version of Git for Windows" link.
3. Download the installer and follow the instructions to install the software. You can mostly use the defaults when
installing, but I recommend changing the default text editor used by Git to Notepad (not Notepad++). When the installer
asks for for the name of the initial branch in new repositories, you can select whatever option you want. "Let git decide"
is the current default, otherwise you can use the radio button to override the default branch name for new repositories.
"main" is a popular alternate choice. You should be able to use all the other default settings.
4. When you get to the install button, click "Install". When the installation has completed click "Finish". 
5. Close your command prompt window and re-open it. When you re-open the window and type "git", you should see a usage
message with a list of git subcommands.

### Choosing a place to save this program

You'll need to figure out a place to store this program on your computer. For the instructions below I assume you'll want
to put this program in a directory called "src" that lives on your desktop. 

1. At the command prompt, switch to the c: drive.
```console
c:
```
2. Navigate to that directory. In the command below, replace USERNAME with your username (e.g., "jej".)
```console
cd Users\USERNAME\Desktop
```
3. Make a new directory called "src" and navigate to that directory.
```console
mkdir src
cd src
```
4. Make a new directory, called "campus_publications_validator" and navigate to that directory.
```console
mkdir campus_publications_validator
cd campus_publications_validator
```
5. Make a Python virtual environment for this script. This code requires some third party libraries, and
the virtual environment will help make sure those libraries don't conflict with others that have been
installed on your computer.
```console
python -m venv venv
venv\Scripts\activate
```
When you start the virtual environment, the command prompt should begin with the string "(venv)". 
6. Clone the git repository for this project on your local machine.
```console
git clone https://github.com/johnjung/campus_publications_validator
cd campus_publications_validator
```
7. Install requirements for this project.
```console
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
