/*
Create Tables
*/

CREATE SCHEMA api;

CREATE TABLE IF NOT EXISTS api.DiscordGuilds (
	Guild_Id BIGINT,
	Guild_Name VARCHAR(100),
	PRIMARY KEY(Guild_Id)
);

CREATE TABLE IF NOT EXISTS api.DiscordChannels (
	Channel_Id BIGINT,
	Channel_Name VARCHAR(100),
	PRIMARY KEY(Channel_Id)
);

CREATE TABLE IF NOT EXISTS api.DiscordUsers (
	User_Id BIGINT,
	User_Name VARCHAR(100),
	PRIMARY KEY(User_Id)
);

CREATE TABLE IF NOT EXISTS api.DiscordMessages (
	Message_Id BIGINT,
	Guild_Id BIGINT,
	Channel_Id BIGINT,
	User_Id BIGINT,
	Message VARCHAR(4000),
	Message_Timestamp TIMESTAMP,
	PRIMARY KEY(Message_Id),
	CONSTRAINT Guild_Id FOREIGN KEY(Guild_Id) REFERENCES api.DiscordGuilds(Guild_Id),
	CONSTRAINT Channel_Id FOREIGN KEY(Channel_Id) REFERENCES api.DiscordChannels(Channel_Id),
	CONSTRAINT User_Id FOREIGN KEY(User_Id) REFERENCES api.DiscordUsers(User_Id)
);

/*
Create Function for adding data to the database
*/
CREATE FUNCTION api.add_message(c_id bigint, c_name text, g_id bigint, g_name text, u_id bigint, u_name text, msg_id text, msg text,  msg_timestamp text)
RETURNS VOID
LANGUAGE PLPGSQL
AS
$$
DECLARE
g_name2 TEXT;
c_name2 TEXT;
u_name2 TEXT;
BEGIN
SELECT Guild_Name INTO g_name2 FROM api.DiscordGuilds WHERE Guild_Id = g_id;
IF NOT FOUND THEN
    INSERT INTO api.DiscordGuilds VALUES (g_id, g_name);
ELSIF g_name <> g_name2 THEN
    UPDATE api.DiscordGuilds SET Guild_Name = g_name WHERE Guild_Id = g_id;
END IF;
SELECT Channel_Name INTO c_name2 FROM api.DiscordChannels WHERE Channel_Id = c_id;
IF NOT FOUND THEN
    INSERT INTO api.DiscordChannels VALUES (c_id, c_name);
ELSIF c_name <> c_name2 THEN
    UPDATE api.DiscordChannels SET Channel_Name = c_name WHERE Channel_Id = c_id;
END IF;
SELECT User_Name INTO u_name2 FROM api.DiscordUsers WHERE User_Id = u_id;
IF NOT FOUND THEN
    INSERT INTO api.DiscordUsers VALUES (u_id, u_name);
ELSIF u_name <> u_name2 THEN
    UPDATE api.DiscordUsers SET User_Name = u_name WHERE User_Id = u_id;
END IF;

IF EXISTS (SELECT * FROM api.DiscordMessages WHERE Message_Id = CAST (msg_id AS BIGINT)) THEN
    UPDATE api.DiscordMessages SET Guild_Id = g_id, Channel_Id = c_id, User_Id = u_id, Message = msg, Message_Timestamp = TO_TIMESTAMP(msg_timestamp, 'YYYY-MM-DD HH24:MI:SS') WHERE Message_Id = CAST (msg_id AS BIGINT);
ELSE
    INSERT INTO api.DiscordMessages VALUES (CAST(msg_id AS BIGINT), g_id, c_id, u_id, msg, TO_TIMESTAMP(msg_timestamp, 'YYYY-MM-DD HH24:MI:SS'));

END IF;

END;
$$;


/*
Create Views for viewing the data in the database
*/

CREATE VIEW api.FullView AS SELECT * FROM api.DiscordMessages NATURAL JOIN api.DiscordGuilds NATURAL JOIN api.DiscordChannels NATURAL JOIN api.DiscordUsers;

CREATE VIEW api.UserMessagesTotal AS SELECT User_Id, User_Name, Count(*) FROM api.DiscordMessages NATURAL JOIN api.DiscordUsers GROUP BY User_Id, User_Name;

CREATE VIEW api.UserMessagesByGuild AS SELECT User_Id, User_Name, Guild_Id, Guild_Name, Count(*) FROM api.DiscordMessages NATURAL JOIN api.DiscordUsers NATURAL JOIN api.DiscordGuilds GROUP BY User_Id, User_Name, Guild_Id, Guild_Name;

CREATE VIEW api.UserMessagesByChannel AS SELECT User_Id, User_Name, Guild_Id, Guild_Name, Channel_Id, Channel_Name, Count(*) FROM api.FullView GROUP BY User_Id, User_Name, Guild_Id, Guild_Name, Channel_Id, Channel_Name;

CREATE VIEW api.MessagesByChannel AS SELECT Channel_Id, Channel_Name, Guild_Id, Guild_Name, Count(*) FROM api.DiscordMessages NATURAL JOIN api.DiscordChannels NATURAL JOIN api.DiscordGuilds GROUP BY Channel_Id, Channel_Name, Guild_Id, Guild_Name;


/*
Roles and permissions
*/
CREATE ROLE vege nologin;

GRANT USAGE ON SCHEMA api TO vege;
GRANT ALL ON api.DiscordMessages to vege;
GRANT ALL ON api.DiscordChannels to vege;
GRANT ALL ON api.DiscordUsers to vege;
GRANT ALL ON api.DiscordGuilds to vege;
GRANT ALL ON FUNCTION api.add_message to vege;
GRANT ALL ON api.FullView to vege;
GRANT ALL ON api.UserMessagesTotal to vege;
GRANT ALL ON api.UserMessagesByGuild to vege;
GRANT ALL ON api.UserMessagesByChannel to vege;
GRANT ALL ON api.MessagesByChannel to vege;

GRANT vege TO auth;