python ticket_gen.py -n 1000 -o activities.json
python store_activities.py -i activities.json -o Ticket.db
sqlite3 Ticket.db ".read ticket_status.sql"
PAUSE