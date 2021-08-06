#! /bin/bash

set -e

# Always overwrite the .env file, it's created during the image build and
# doesn't have the required handlers.
cat <<EOF > /opt/asylum/.env
DATABASE_URL=postgres://asylum:asylum@localhost/asylum
MEMBERAPPLICATION_CALLBACKS_HANDLER=hhlcallback.handlers.ApplicationHandler
RECURRINGTRANSACTIONS_CALLBACKS_HANDLER=hhlcallback.handlers.RecurringTransactionsHolviHandler
TRANSACTION_CALLBACKS_HANDLER=hhlcallback.handlers.TransactionHandler
NORDEA_BARCODE_IBAN=FI 21 123456 0000078 5
SLACK_INVITE_LINK=https://www.example.com/this-is-a-fake-slack-invite
EOF

VENV_DIR_PATH=/opt/asylum-venv/

# activate virtualenv
. $VENV_DIR_PATH/bin/activate

# make sure postgresql is running
sudo -u postgres service postgresql start
set +e
export PGPASSWORD=asylum; while true; do psql -q asylum -c 'SELECT 1;' 1>/dev/null 2>&1 ; if [ "$?" -ne "0" ]; then echo "Waiting for psql"; sleep 1; else break; fi; done
set -e

# Start forego or execute a command in the virtualenv
if [ "$#" -eq 0 ]; then
  echo "Starting devel server"
  maildump --http-ip 0.0.0.0 -p ~/maildump.pid &
  npm run build
  npm run watch &
  NPM=$!
  ./manage.py runserver 0.0.0.0:8000
  maildump -p ~/maildump.pid --stop
else
  echo "Calling $@"
  /usr/bin/env "$@"
fi
