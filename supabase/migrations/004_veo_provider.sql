-- Migrate legacy provider references to Gemini Veo
UPDATE media_assets SET provider = 'veo' WHERE provider IN ('pixverse', 'higgsfield');
