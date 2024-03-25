# fundamental analysis data scrapping - python
This script can be used to scrap the fundamental data of any company available in the screener.in website by providing the list of company codes.
The script can be run in a linux machine / windows machine / MAC manually or through a cron job.

Setup:

Steps to run the script -
    1. Install python2 or python3 latest version in your system. Prefer python3 to avoid any dependency related issues.

    2. Create a venv if you don't want to make any changes in your current env libraries. Use below commands to create your env -
        python3 -m venv custom_venv or python -m venv custom_venv

    3. Activate the venv in the system using below command -
        On Windows : custom_venv\Scripts\activate
        On Linux/Mac : source custom_venv/bin/activate

    4. Install all the dependencies mentioned in the requirements.txt present in the repo using below command -
        pip install -r requirements.txt

    5. Run the python script using below command -
        Note: Make sure to create an account on screener.in. Without it all the metrics will not be available.

        python get_screener_data.py # This way the script scraps data for reliance,havells,TATACONSUM companies by default.
        python get_screener_data.py -cl reliance,havells # This way the script scraps data for reliance and havells by default.
        python get_screener_data.py -u <login_user_name> -p <login_password> # This way the script logs into the specific user account to scrap data.

        Use help command to see supported arguments with get_screener_data.py -> python get_screener_data.py -h

    6. Check all the scrapped data stored in the path '/tmp' by default. The files are saved with the company code with the name <company_code>.txt and <company_code>.yaml. Specify your own custom path using below command -
        python get_screener_data.py -fd <custom_path>
