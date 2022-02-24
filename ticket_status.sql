/*
	ticket_status.sql: Used to add ticket status time information to the Freshdesk ticket database.
	
	Author: Alexander Palegeorge
	Date: 1/12/2021

*/

DROP TABLE IF EXISTS StatusTime;
CREATE TABLE StatusTime(
	ticket_id						INT PRIMARY KEY NOT NULL,
	time_spent_open					TEXT,
	time_spent_waiting_on_customer	TEXT,
	time_spent_waiting_for_response	TEXT,
	time_till_resolution			TEXT,
	time_to_first_response			TEXT
	);

	
-- Populates the temporary working table with data from the join and select statement	
DROP TABLE IF EXISTS temp.WorkingData;
CREATE TEMP TABLE WorkingData(
	ticket_id,
	time_ticket_created,
	performed_at,
	status
);
INSERT INTO WorkingData
	SELECT 	ticket_id, time_ticket_created, performed_at, status 
	FROM
		-- Selects all necessary working data from Tickets and Task
		(
			SELECT ticket_id, time_ticket_created, performed_at
			FROM Tickets 
			WHERE task_id NOT NULL
		) 
		AS Tic
		INNER JOIN 
		(
			SELECT ticket_id AS task_ticket_id, status 
			FROM Task
		) 
		AS Tas
		ON Tic.ticket_id = Tas.task_ticket_id
	ORDER BY status ASC;
	

-- Create temporary time_to_first_response data
DROP TABLE IF EXISTS id_ttfr;		
CREATE TEMP TABLE id_ttfr (
	ticket_id,
	time_to_first_response
);
INSERT INTO id_ttfr
	SELECT
		ticket_id,
		(
			SELECT strftime('%s', datetime(
								substr(performed_at, 7, 4) || '-' || 
								substr(performed_at, 4, 2) || '-' || 
								substr(performed_at, 1, 2) || ' ' ||
								substr(performed_at, 12, 8)
							 ), 'utc'
					  )
			- strftime('%s', datetime(
								substr(time_ticket_created, 7, 4) || '-' || 
								substr(time_ticket_created, 4, 2) || '-' || 
								substr(time_ticket_created, 1, 2) || ' ' ||
								substr(time_ticket_created, 12, 8)
							 ), 'utc'
					  ) 
		)
		AS time_to_first_response
	FROM WorkingData;
	

-- Create temporary time_spent_open data	
DROP TABLE IF EXISTS id_tso;
CREATE TEMP TABLE id_tso (
	id,
	time_spent_open
);
INSERT INTO id_tso
	SELECT 
		ticket_id AS id,
			(
				SELECT strftime('%s', 'now')
				- strftime('%s', datetime(
									substr(time_ticket_created, 7, 4) || '-' || 
									substr(time_ticket_created, 4, 2) || '-' || 
									substr(time_ticket_created, 1, 2) || ' ' ||
									substr(time_ticket_created, 12, 8)
								 ), 'utc'
						  )
			) AS time_spent_open
	FROM WorkingData
	WHERE status = 'Open';
	
	
-- Create temporary time_spent_waiting_on_customer data
DROP TABLE IF EXISTS id_tswoc;
CREATE TEMP TABLE id_tswoc (
	id,
	time_spent_waiting_on_customer
);
INSERT INTO id_tswoc
	SELECT
		ticket_id AS id,
		(
			SELECT strftime('%s', 'now')
						- strftime('%s', datetime(
											substr(performed_at, 7, 4) || '-' || 
											substr(performed_at, 4, 2) || '-' || 
											substr(performed_at, 1, 2) || ' ' ||
											substr(performed_at, 12, 8)
										 ), 'utc'
								  )
		) AS time_spent_waiting_on_customer
		FROM WorkingData
		WHERE status = 'Waiting for Customer';


-- Create temporary time_spend_waiting_for_response data
DROP TABLE IF EXISTS id_tswfr;
CREATE TEMP TABLE id_tswfr (
	id,
	time_spent_waiting_for_response
);
INSERT INTO id_tswfr
	SELECT
		ticket_id AS id,
		(
			SELECT strftime('%s', 'now')
						- strftime('%s', datetime(
											substr(performed_at, 7, 4) || '-' || 
											substr(performed_at, 4, 2) || '-' || 
											substr(performed_at, 1, 2) || ' ' ||
											substr(performed_at, 12, 8)
										 ), 'utc'
								  )
		) AS time_spent_waiting_on_customer
		FROM WorkingData
		WHERE status = 'Pending';		


-- Create temporary time_till_resolution data
DROP TABLE IF EXISTS id_ttr;		
CREATE TEMP TABLE id_ttr (
	id,
	time_till_resolution
);
INSERT INTO id_ttr
	SELECT
		ticket_id AS id,
		(
			SELECT strftime('%s', datetime(
								substr(performed_at, 7, 4) || '-' || 
								substr(performed_at, 4, 2) || '-' || 
								substr(performed_at, 1, 2) || ' ' ||
								substr(performed_at, 12, 8)
							 ), 'utc'
					  )
			- strftime('%s', datetime(
								substr(time_ticket_created, 7, 4) || '-' || 
								substr(time_ticket_created, 4, 2) || '-' || 
								substr(time_ticket_created, 1, 2) || ' ' ||
								substr(time_ticket_created, 12, 8)
							 ), 'utc'
					  ) 
		)
		AS time_till_resolution
	FROM WorkingData
	WHERE status = 'Resolved';

	
-- Add ticket status time data to StatusTime
INSERT INTO StatusTime
	SELECT * FROM (
		-- Join all newly created data	
		SELECT
			ticket_id,
			time_spent_open,
			time_spent_waiting_on_customer,
			time_spent_waiting_for_response,
			time_till_resolution,
			time_to_first_response
			FROM
				id_ttfr
				LEFT OUTER JOIN
				id_tso
				ON id_ttfr.ticket_id = id_tso.id
				LEFT OUTER JOIN
				id_tswoc
				ON id_ttfr.ticket_id = id_tswoc.id
				LEFT OUTER JOIN
				id_tswfr
				ON id_ttfr.ticket_id = id_tswfr.id
				LEFT OUTER JOIN
				id_ttr
				ON id_ttfr.ticket_id = id_ttr.id
			ORDER BY 
				time_spent_open	DESC,
				time_spent_waiting_on_customer DESC,
				time_spent_waiting_for_response DESC,
				time_till_resolution DESC
	);
	

-- Drop all temporary entities
DROP TABLE id_ttfr;
DROP TABLE id_tso; 
DROP TABLE id_tswfr;
DROP TABLE id_tswoc;
DROP TABLE id_ttr;
DROP TABLE WorkingData;

