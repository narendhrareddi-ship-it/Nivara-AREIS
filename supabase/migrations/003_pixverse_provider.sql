-- Migrate legacy Higgsfield provider references to PixVerse
UPDATE media_assets SET provider = 'pixverse' WHERE provider = 'higgsfield';
