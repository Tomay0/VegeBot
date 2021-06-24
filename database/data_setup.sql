/*
This sets up the whole database in PostgreSQL.

Note that the authentication password needs to be updated here
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

CREATE FUNCTION api.add_message(args JSON)
RETURNS VOID
LANGUAGE PLPGSQL
AS
$$
DECLARE
g_name TEXT;
c_name TEXT;
u_name TEXT;
BEGIN
SELECT Guild_Name INTO g_name FROM api.DiscordGuilds WHERE Guild_Id = CAST (args->>'guild_id' AS BIGINT);
IF NOT FOUND THEN
    INSERT INTO api.DiscordGuilds VALUES (CAST (args->>'guild_id' AS BIGINT), args->>'guild_name');
ELSIF g_name <> args->>'guild_name' THEN
    UPDATE api.DiscordGuilds SET Guild_Name = args->>'guild_name' WHERE Guild_Id = CAST (args->>'guild_id' AS BIGINT);
END IF;
SELECT Channel_Name INTO c_name FROM api.DiscordChannels WHERE Channel_Id = CAST (args->>'channel_id' AS BIGINT);
IF NOT FOUND THEN
    INSERT INTO api.DiscordChannels VALUES (CAST (args->>'channel_id' AS BIGINT), args->>'channel_name');
ELSIF c_name <> args->>'channel_name' THEN
    UPDATE api.DiscordChannels SET Channel_Name = args->>'channel_name' WHERE Channel_Id = CAST (args->>'channel_id' AS BIGINT);
END IF;
SELECT User_Name INTO u_name FROM api.DiscordUsers WHERE User_Id = CAST (args->>'user_id' AS BIGINT);
IF NOT FOUND THEN
    INSERT INTO api.DiscordUsers VALUES (CAST (args->>'user_id' AS BIGINT), args->>'user_name');
ELSIF u_name <> args->>'user_name' THEN
    UPDATE api.DiscordUsers SET User_Name = args->>'user_name' WHERE User_Id = CAST (args->>'user_id' AS BIGINT);
END IF;

IF EXISTS (SELECT * FROM api.DiscordMessages WHERE Message_Id = CAST (args->>'message_id' AS BIGINT)) THEN
    UPDATE api.DiscordMessages SET Guild_Id = args->>'guild_id', Channel_Id = args->>'channel_id', User_Id = args->>'user_id', Message = args->>'message', Message_Timestamp = TO_TIMESTAMP(args->>'message_timestamp', 'YYYY-MM-DD HH24:MI:SS') WHERE Message_Id = args->>'message_id';
ELSE
    INSERT INTO api.DiscordMessages VALUES (CAST(args->>'message_id' AS BIGINT), CAST(args->>'guild_id' AS BIGINT), CAST(args->>'channel_id' AS BIGINT), CAST(args->>'user_id' AS BIGINT), args->>'message', TO_TIMESTAMP(args->>'message_timestamp', 'YYYY-MM-DD HH24:MI:SS'));

END IF;

END;
$$;

CREATE ROLE vege nologin;

GRANT USAGE ON SCHEMA api TO vege;
GRANT ALL ON api.DiscordMessages to vege;
GRANT ALL ON api.DiscordChannels to vege;
GRANT ALL ON api.DiscordUsers to vege;
GRANT ALL ON api.DiscordGuilds to vege;
GRANT ALL ON api.add_messages to vege;

GRANT vege TO auth;