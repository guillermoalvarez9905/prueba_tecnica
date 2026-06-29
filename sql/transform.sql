CREATE TABLE IF NOT EXISTS `prueba-tecnica-500721.INTEGRATION.integration_prueba_tecnica` (
    id_player           STRING NOT NULL,
    str_player          STRING,
    str_nationality     STRING,
    str_team            STRING,
    str_position        STRING,
    date_born           STRING,
    str_sport           STRING,
    age                 INT64,
    transformation_date DATE
);

MERGE `prueba-tecnica-500721.INTEGRATION.integration_prueba_tecnica` AS target
USING (
    SELECT
        id_player,
        str_player,
        str_nationality,
        str_team,
        str_position,
        date_born,
        str_sport,
        DATE_DIFF(CURRENT_DATE(), SAFE.PARSE_DATE('%Y-%m-%d', date_born), YEAR) AS age,
        CURRENT_DATE() AS transformation_date
    FROM `prueba-tecnica-500721.SANDBOX_FOOTBALL_PLAYERS.players`
    WHERE str_position NOT IN ('Assistant Coach', 'Manager')
      AND DATE_DIFF(CURRENT_DATE(), SAFE.PARSE_DATE('%Y-%m-%d', date_born), YEAR) < 30
      AND str_nationality != ''
    QUALIFY ROW_NUMBER() OVER (PARTITION BY id_player ORDER BY ingestion_timestamp DESC) = 1
) AS source
ON target.id_player = source.id_player
WHEN MATCHED THEN
    UPDATE SET
        str_player      = source.str_player,
        str_nationality = source.str_nationality,
        str_team        = source.str_team,
        str_position    = source.str_position,
        date_born       = source.date_born,
        str_sport           = source.str_sport,
        age                 = source.age,
        transformation_date = source.transformation_date
WHEN NOT MATCHED BY SOURCE THEN DELETE
WHEN NOT MATCHED THEN
    INSERT (
        id_player, 
        str_player, 
        str_nationality, 
        str_team,
        str_position, 
        date_born, 
        str_sport, 
        age, 
        transformation_date
    )
    VALUES (
        source.id_player, 
        source.str_player, 
        source.str_nationality, 
        source.str_team,
        source.str_position, 
        source.date_born, 
        source.str_sport, 
        source.age, 
        source.transformation_date
    );
