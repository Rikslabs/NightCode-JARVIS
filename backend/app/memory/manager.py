import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory.json"


class MemoryManager:
    def load(self):
        """
        Safely loads memory from the JSON file.
        - If the file doesn't exist, is empty, or contains invalid JSON,
          it returns a default empty dictionary.
        """
        try:
            if not MEMORY_FILE.exists():
                return {}
            with open(MEMORY_FILE, "r") as f:
                content = f.read()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            # Return a default structure on error to prevent crashes
            return {}

    def save(self, data):
        """
        Safely saves data to the JSON file using an atomic write operation.
        - Writes to a temporary file first.
        - Renames the temporary file to the final destination, which is an
          atomic operation on most OSes, preventing data loss on crash.
        """
        temp_file = MEMORY_FILE.with_suffix(".json.tmp")
        try:
            with open(temp_file, "w") as f:
                json.dump(data, f, indent=4)
            temp_file.replace(MEMORY_FILE)
        except IOError as e:
            # Handle potential file system errors during write/rename
            print(f"Error saving memory: {e}")