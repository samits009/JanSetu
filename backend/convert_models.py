import os
import glob

models_dir = r"d:\Development Drive\JanSetu\backend\app\models"
files = glob.glob(os.path.join(models_dir, "*.py"))

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    if 'sqlalchemy.dialects.postgresql' in content:
        content = content.replace(
            "from sqlalchemy.dialects.postgresql import UUID, JSONB",
            "from sqlalchemy import Uuid as UUID, JSON as JSONB"
        )
        content = content.replace(
            "from sqlalchemy.dialects.postgresql import JSONB, UUID",
            "from sqlalchemy import JSON as JSONB, Uuid as UUID"
        )
        content = content.replace(
            "from sqlalchemy.dialects.postgresql import UUID",
            "from sqlalchemy import Uuid as UUID"
        )
        content = content.replace(
            "from sqlalchemy.dialects.postgresql import JSONB",
            "from sqlalchemy import JSON as JSONB"
        )
        with open(f, 'w') as file:
            file.write(content)
            print(f"Updated {f}")
