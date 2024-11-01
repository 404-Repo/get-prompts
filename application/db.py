from contextlib import contextmanager
from pathlib import Path
from typing import List, Generator

import bittensor as bt
import psycopg2
from psycopg2.extensions import connection as psycopg2_conn
from psycopg2.extras import execute_values


class PromptsDB:
    """Database handler for prompts storage."""

    def __init__(self, config: bt.config) -> None:
        """Initialize database connection and structure.

        Args:
            config: Bittensor configuration object containing database credentials
        """
        self.config = config
        # self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[psycopg2_conn, None, None]:
        """Get a database connection using context manager for automatic cleanup.

        Yields:
            psycopg2.connection: Database connection object
        """
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.config.pg_host,
                port=self.config.pg_port,
                database=self.config.pg_database,
                user=self.config.pg_user,
                password=self.config.pg_password,
            )
            yield conn
        finally:
            if conn is not None:
                conn.close()

    def _init_db(self) -> None:
        """Initialize database connection and create table if not exists."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS prompts (
                            id SERIAL PRIMARY KEY,
                            prompt TEXT NOT NULL,
                            date_creation TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                            validation_status VARCHAR(10) NOT NULL CHECK (validation_status IN ('wait', 'validated', 'failed')),
                            generator_id VARCHAR(15),
                            last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE (prompt, generator_id)
                        )
                        """
                    )
                conn.commit()
        except Exception as e:
            bt.logging.error(f"Failed to initialize database: {str(e)}")
            raise

    def upload_prompts(self, prompts: List[str], generator_id: str) -> None:
        """Upload a batch of prompts to the database.

        Args:
            prompts: List of prompts to upload
            generator_id: IP address of the prompt generator
        """
        if not prompts:
            return

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        """
                        INSERT INTO prompts (prompt, validation_status, generator_id)
                        VALUES %s
                        ON CONFLICT (prompt, generator_id) DO NOTHING
                        """,
                        [(prompt, "wait", generator_id) for prompt in prompts],
                    )
                conn.commit()

            bt.logging.info(f"Successfully uploaded {len(prompts)} prompts to database")

        except Exception as e:
            bt.logging.error(f"Failed to upload prompts to database: {str(e)}")
            raise

    def upload_from_files(self, file_paths: List[str], generator_id: str) -> None:
        """Upload prompts from multiple files to the database.

        Args:
            file_paths: List of paths to files containing prompts
            generator_id: IP address of the prompt generator
        """
        try:
            total_uploaded = 0
            with self._get_connection() as conn:
                for file_path in file_paths:
                    with Path(file_path).open(encoding='utf-8') as f:
                        prompts = [line.strip("\n") for line in f if line.strip()]

                    with conn.cursor() as cur:
                        execute_values(
                            cur,
                            """
                            INSERT INTO prompts (prompt, validation_status, generator_id)
                            VALUES %s
                            ON CONFLICT (prompt, generator_id) DO NOTHING
                            """,
                            [(prompt, "wait", generator_id) for prompt in prompts],
                        )
                        total_uploaded += len(prompts)
                    conn.commit()

            bt.logging.info(f"Successfully uploaded {total_uploaded} prompts from {len(file_paths)} files")

        except Exception as e:
            bt.logging.error(f"Failed to upload files to database: {str(e)}")
            raise

    def update_validation_status(self, prompt_id: int, status: str) -> None:
        """Update the validation status of a prompt.

        Args:
            prompt_id: ID of the prompt to update
            status: New validation status ('wait', 'validated', or 'failed')
        """
        if status not in ('wait', 'validated', 'failed'):
            raise ValueError("Status must be one of: wait, validated, failed")

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE prompts 
                        SET validation_status = %s, last_updated = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (status, prompt_id)
                    )
                conn.commit()

            bt.logging.info(f"Successfully updated validation status to {status} for prompt {prompt_id}")

        except Exception as e:
            bt.logging.error(f"Failed to update validation status: {str(e)}")
            raise
