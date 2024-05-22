# Extract messages
pybabel extract -F agrimar/babel.cfg -o agrimar/messages.pot agrimar

# Initialize translations
pybabel init -i agrimar/messages.pot -d agrimar/translations -l en
pybabel init -i agrimar/messages.pot -d agrimar/translations -l fr
pybabel init -i agrimar/messages.pot -d agrimar/translations -l ar

# Compile translations
pybabel compile -d agrimar/translations
