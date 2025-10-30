import sqlite3
import shutil
import os


class DatabaseManager:
    def __init__(self, db_file="reading_tracker.db"):
        """Initialize and connect to the SQLite database."""
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key cascade
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        """
        Create the necessary tables if they don't exist.
        --- NEW: Also checks for and adds missing columns to 'items' table ---
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            display_order INTEGER,
            FOREIGN KEY (parent_id) REFERENCES items(id) ON DELETE CASCADE
        )
        """)

        # --- NEW: Schema Migration ---
        # Define all columns that *should* exist
        expected_columns = {
            "is_assignment": "INTEGER DEFAULT 0",
            "project_purpose_text": "TEXT",
            "project_goals_text": "TEXT",
            "key_questions_text": "TEXT",
            "thesis_text": "TEXT",
            "insights_text": "TEXT",
            "unresolved_text": "TEXT"
        }

        # Get existing columns
        self.cursor.execute("PRAGMA table_info(items)")
        existing_columns = [row['name'] for row in self.cursor.fetchall()]

        # Add any missing columns
        for col_name, col_type in expected_columns.items():
            if col_name not in existing_columns:
                try:
                    print(f"Adding missing column: {col_name}...")
                    self.cursor.execute(f"ALTER TABLE items ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError as e:
                    print(f"Warning: Could not add column {col_name}. {e}")
        # --- END NEW ---

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS instructions (
            project_id INTEGER PRIMARY KEY,
            key_questions_instr TEXT NOT NULL,
            thesis_instr TEXT NOT NULL,
            insights_instr TEXT NOT NULL,
            unresolved_instr TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES items(id) ON DELETE CASCADE
        )
        """)
        # --- END NEW TABLE ---

        self.conn.commit()

    # --- NEW FUNCTION: GET/CREATE INSTRUCTIONS ---
    def get_or_create_instructions(self, project_id):
        """
        Gets instructions for a project. If they don't exist,
        creates and returns the default instructions.
        """
        self.cursor.execute("SELECT * FROM instructions WHERE project_id = ?", (project_id,))
        instr = self.cursor.fetchone()

        if instr:
            return instr
        else:
            # Defaults
            defaults = {
                "project_id": project_id,
                "key_questions_instr": "What is the central question this project aims to answer?",
                "thesis_instr": "State your current working thesis/argument.",
                "insights_instr": "Capture 3-7 key insights that are shaping your thinking.",
                "unresolved_instr": "List open questions, unresolved questions, or uncertainties to be revisited."
            }
            self.cursor.execute("""
                INSERT INTO instructions 
                (project_id, key_questions_instr, thesis_instr, insights_instr, unresolved_instr)
                VALUES (:project_id, :key_questions_instr, :thesis_instr, :insights_instr, :unresolved_instr)
            """, defaults)
            self.conn.commit()

            # Fetch and return the newly created row
            self.cursor.execute("SELECT * FROM instructions WHERE project_id = ?", (project_id,))
            return self.cursor.fetchone()

    # --- NEW FUNCTION: UPDATE INSTRUCTIONS ---
    def update_instructions(self, project_id, key_questions, thesis, insights, unresolved):
        """Updates the instruction text for a given project."""
        self.cursor.execute("""
            UPDATE instructions
            SET key_questions_instr = ?, thesis_instr = ?, insights_instr = ?, unresolved_instr = ?
            WHERE project_id = ?
        """, (key_questions, thesis, insights, unresolved, project_id))
        self.conn.commit()

    # --- NEW FUNCTION: UPDATE A SINGLE TEXT FIELD ---
    def update_project_text_field(self, project_id, field_name, content):
        """
        Dynamically updates a single text field for a project in the items table.
        This is used for auto-saving text boxes.
        """
        # Securely build query to prevent SQL injection
        if field_name not in ['project_purpose_text', 'project_goals_text',
                              'key_questions_text', 'thesis_text',
                              'insights_text', 'unresolved_text']:
            print(f"Error: Invalid field name {field_name}")
            return

        # Use f-string to safely insert the column name
        query = f"UPDATE items SET {field_name} = ? WHERE id = ?"
        self.cursor.execute(query, (content, project_id))
        self.conn.commit()

    # --- END NEW FUNCTIONS ---

    def get_items(self, parent_id=None):
        """
        Get all items under a specific parent.
        If parent_id is None, gets root items (standalone projects and classes).
        """
        query = "SELECT * FROM items WHERE parent_id IS ? ORDER BY display_order"
        params = (parent_id,)
        if parent_id is None:
            query = "SELECT * FROM items WHERE parent_id IS NULL ORDER BY display_order"
            params = ()

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def create_item(self, name, item_type, parent_id=None, is_assignment=1):
        """
        Create a new class or project.
        Calculates the new display_order.
        """
        # Get max display_order for the current parent
        query = "SELECT MAX(display_order) FROM items WHERE parent_id IS ?"
        params = (parent_id,)
        if parent_id is None:
            query = "SELECT MAX(display_order) FROM items WHERE parent_id IS NULL"
            params = ()

        self.cursor.execute(query, params)
        max_order = self.cursor.fetchone()[0]
        new_order = 0 if max_order is None else max_order + 1

        self.cursor.execute(
            "INSERT INTO items (parent_id, type, name, display_order, is_assignment) VALUES (?, ?, ?, ?, ?)",
            (parent_id, item_type, name, new_order, is_assignment)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def rename_item(self, item_id, new_name):
        """Rename an existing item."""
        self.cursor.execute("UPDATE items SET name = ? WHERE id = ?", (new_name, item_id))
        self.conn.commit()

    def move_item(self, item_id, new_parent_id=None):
        """
        Move an item to a new parent (or to root if new_parent_id is None).
        This also recalculates its display_order to put it at the end of the new list.
        """
        # Get max display_order for the new parent
        query = "SELECT MAX(display_order) FROM items WHERE parent_id IS ?"
        params = (new_parent_id,)
        if new_parent_id is None:
            query = "SELECT MAX(display_order) FROM items WHERE parent_id IS NULL"
            params = ()

        self.cursor.execute(query, params)
        max_order = self.cursor.fetchone()[0]
        new_order = 0 if max_order is None else max_order + 1

        self.cursor.execute(
            "UPDATE items SET parent_id = ?, display_order = ? WHERE id = ?",
            (new_parent_id, new_order, item_id)
        )
        self.conn.commit()

    def update_order(self, ordered_db_ids):
        """
        Updates the display_order for a list of item IDs.
        The list is assumed to be in the new correct order.
        """
        for index, item_id in enumerate(ordered_db_ids):
            self.cursor.execute("UPDATE items SET display_order = ? WHERE id = ?", (index, item_id))
        self.conn.commit()

    def get_item_details(self, item_id):
        """Get all details for a single item by its ID."""
        self.cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        return self.cursor.fetchone()

    # --- NEW METHODS ---

    def delete_item(self, item_id):
        """
        Delete an item.
        If it's a class, ON DELETE CASCADE will handle deleting its children.
        """
        self.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()

    def get_all_classes(self):
        """Get a list of all classes, used for the 'Move' dialog."""
        self.cursor.execute("SELECT id, name FROM items WHERE type = 'class' ORDER BY name")
        return self.cursor.fetchall()

    def duplicate_item(self, item_id, new_parent_id=None):
        """
        Recursively duplicates an item (project or class).
        If new_parent_id is provided, it's used as the parent for the new copy.
        If not, the original's parent_id is used.
        """
        # 1. Get original item's data
        original = self.get_item_details(item_id)
        if not original:
            return

        # 2. Determine the parent for the new copy
        parent_id = new_parent_id if new_parent_id is not None else original['parent_id']

        # 3. Create the new item (the copy)
        new_name = f"{original['name']} (Copy)"
        new_id = self.create_item(
            new_name,
            original['type'],
            parent_id,
            original['is_assignment']
        )

        # 4. If it was a class, recursively duplicate its children
        if original['type'] == 'class':
            children = self.get_items(original['id'])
            for child in children:
                # Pass the *new* class's ID as the new_parent_id
                self.duplicate_item(child['id'], new_parent_id=new_id)

    def __del__(self):
        """Close the database connection on object deletion."""
        self.conn.close()



