
apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
su postgres -c 'createuser -dRS vagrant'
