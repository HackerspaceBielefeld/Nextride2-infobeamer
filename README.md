# Nextride2-infobeamer
Nextride2-infobeamer is an extension for [Nextride2](https://github.com/HackerspaceBielefeld/Nextride2) and implements a simple solution to display images on screens running Nextride.
N2i allows you to fetch a schedule and create a queue from the url elements. Those ressources are than itteratively displayed on the Nextride screens.
N2i also implements a CMS for user uploaded date. This can be used to allow guests and visitors to upload slides/ads thay want to share.

## Restrictions
Please note! As N2i is currently under development not all features work reliable. It's not ready to be deployed in production.
Please use the latest release for a stable and secure version of N2i.

## Todos
* remove id from filehandler and db_helper methods as filename is enough
* clean and fix delete_file in filehandler.
* connect the user method remove_user_file with delete file. This ensures the status is syncted.
* Adjust the dashboard to only show users files
* Add a button to each image which calls a delete function