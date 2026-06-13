# Local data exports for Supabase import

After running migrations on your Supabase project (`python scripts/connect-supabase.py`), import these files in **Supabase SQL Editor** in this order:

1. `projects.sql`
2. `campaigns.sql`
3. `competitors.sql`
4. `leads.sql`
5. `crm_activity.sql`
6. `social_posts.sql`
7. `media_assets.sql`
8. `bot_logs.sql`

Regenerate from local Postgres:

```bash
./scripts/export-local-to-supabase.sh
```
