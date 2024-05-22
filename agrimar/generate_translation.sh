# Extract messages
pybabel extract -F agrimar/babel.cfg -o messages.pot 
# Initialize translations
pybabel init -i messages.pot -d translations -l en
pybabel init -i messages.pot -d translations -l fr
pybabel init -i messages.pot -d translations -l ar

# Comile translations
pybabel compile -d translations
