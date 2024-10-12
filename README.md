[![Build Chain](https://github.com/HackerspaceBielefeld/Nextride2-infobeamer/actions/workflows/ci.yml/badge.svg)](https://github.com/HackerspaceBielefeld/Nextride2-infobeamer/actions/workflows/ci.yml)

# Nextride2-infobeamer
Nextride2-infobeamer is an extension for [Nextride2](https://github.com/HackerspaceBielefeld/Nextride2) and implements a simple solution to display images on screens running Nextride2. N2i allows you to create a queue of slides which can iteratively be displayed on the Nextride screens. N2i in general implements a CMS for user uploaded date. This can be used to allow guests and visitors to upload slides/ads they want to share. Extensions for N2i extend the CMS and allow full customization of the displayed content. It's also easy to write your own extension.

| Home       | User management |
|------------|-----------------|
| <img src="assets/home.png" width="1920"/> | <img src="assets/management_users.png" width="1920"/> |

## Documentation
Information about N2i are collected in the [wiki](https://github.com/HackerspaceBielefeld/Nextride2-infobeamer/wiki)
while detailled informations about N2i internal functionallity is stored in TO_BE_CREATED.

## Restrictions
Please note! As N2i is currently under development not all features work reliable.
Please use the latest release for a stable and secure version of N2i.

## Todos
General:
* Renew doxygen
    * db_extension_helper.py 10.10.2024
    * db_file_helper.py 10.10.2024
    * db_user_helper.py 10.10.2024
    * emailhandler.py 10.10.2024
    * wsgi.py 04.10.2024
    * role_based_access.py 04.10.2024
    * filehandler.py 10.10.2024
    * helper.py 10.10.2024
    * queuehandler 10.10.2024
* Add instructions for the usage of reverseproxy
* Add better solution for system slides

Extensions:
* Schedule extension
* angle system extension fetching dashboard
* twitter extension
* wether extension
