pybabel extract -o oarepo_requests/translations/messages.pot oarepo_requests
pybabel update -i oarepo_requests/translations/messages.pot -d oarepo_requests/translations
pybabel compile -d oarepo_requests/translations