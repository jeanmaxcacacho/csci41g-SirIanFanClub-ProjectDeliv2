# We've finally made it here! 👋
1. As usual create a virtual environment first, all source files are stored inside the `app` directory. Create your virtual environment OUTSIDE of that folder, same location as `README.md` (this file) and `requirements.txt`. Create the virtual environment via `python -m venv env` as `env/` is the folder name I specified in `.gitignore`.
2. Install all the project dependencies by running `pip install -r requirements.txt`. You can check all the packages your virtual environment currently has access to by running `pip freeze`.
3. Install XAMPP and add it to your system's PATH, the project uses MariaDB as its database and this is made easier to manage via XAMPP. You can test whether or not everything's already running by executing `python app/app.py` to serve the application. If there are no errors you must good to go.

**PROTIP**: When doing back-end stuff (anything server-side/database related) it's good to have 3 active terminals, one for general purpose stuff, another for running the server (changes are applied in a 'hot reload style fashion'), and another connected to the database. This makes it easy to diagnose what your code is currently doing.

4. If you have any questions about what any of the scripts do or which files should belong to which folder PLEASE ask in the GC, the last thing we want is somebody's blunder to set us back multiple days in development time. Generally the source directory names should be self-explanatory. Likewise if writing a new function, *especially a route*, please write a one sentence comment above the definition on what the code is trying to achieve.
5. PLEASE REFRAIN FROM COMMITTING MULTIPLE FILES AT ONCE, DON'T RUN `git add .` but instead run `git add <insert specific file>` instead. In the same spirit when working on a major feature PLEASE MAKE A NEW BRANCH, DON'T PUSH/MERGE CHANGES DIRECTLY TO `main` BEFORE UPDATING THE GC.