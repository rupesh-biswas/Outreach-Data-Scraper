# Outreach Data Scraper

This project is a Python script that helps in retrieving data from the Outreach portal, specifically prospect and user data. It utilizes the official Outreach APIs to fetch the data and saves it into CSV files for further analysis.

## Installation
1. Clone the repository:

```bash
git clone https://github.com/rupesh-biswas/Outreach-Data-Scraper.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage
1. Configure your environment variables by creating a .env file in the root directory of the project and adding the following variables:

```env
email='<your_outreach_email>'
password='<your_outreach_password>'

code_url='<url_from_outreach_developer_portal>'
authUrl='<url_from_outreach_developer_portal>'
token_url='https://api.outreach.io/oauth/token'
```

2. Run the main script outreach-data.py to fetch all prospect and user data:

```bash
python outreach-data.py
```

3. The script will generate two CSV files:
```
outreach_prospects-data.csv: Contains data of all prospects.
outreach-users.csv: Contains data of all users.
```

## Project Structure
- outreach-data.py: Main script to run that fetches data for both prospects and users.

- prospects.py: Module to fetch and process prospect data.

- users.py: Module to fetch and process user data.

## Notes
- Make sure to handle sensitive information such as passwords securely.

- Adjust chunk sizes and other parameters in the scripts as per your requirements.

## License
This project is licensed under the GNU General Public License Version 3, 29 June 2007 - see the LICENSE file for details.
