# Nextride2-infobeamer
Nextride2-infobeamer is an extension for [Nextride2](https://github.com/HackerspaceBielefeld/Nextride2) and implements a simple solution to display images on screens running Nextride.
N2i allows you to fetch a schedule and create a queue from the url elements. Those ressources are than itteratively displayed on the Nextride screens.
N2i also implements a CMS for user uploaded date. This can be used to allow guests and visitors to upload slides/ads thay want to share.

## Setup
1. Clone the repository.
2. Create a new github OAuth application [here](https://github.com/settings/applications/new)
3. Choose a name, the url to the index page and a description
4. As Authorization callback URL use http://yourdomain.tld/auth
5. Register the app
6. Create a file named `.env` in the `html` folder.
7. Enter the information based on the sample file `dot_env_example`.
8. Create a virtual enviroment with: `python -m venv .venv` in the main project folder
9. Activate the venv with: `source .venv/bin/activate`(linux)
10. Install the necessary requirements with `pip install -r requirements.txt`
11. Enter the html folder again and start the application with `python app.py`

## Restrictions
Please note! As N2i is currently under development not all features work reliable.
Please use the latest release for a stable and secure version of N2i.


## Todos
Admin dashboard:
* move role "block" management to role_based_access
  * Add ipban option
Unit testing
* Setup unittests
* Create a CI pipeline