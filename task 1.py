import hashlib
import json
import os

HASH_STORE = "stored_hashes.json"

def calculate_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            return hashlib.sha256(file_data).hexdigest()
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return None

def load_hashes():
    """Load stored hash values from JSON file."""
    if os.path.exists(HASH_STORE):
        with open(HASH_STORE, "r") as f:
            return json.load(f)
    return {}

def save_hashes(hashes):
    """Save hash values to JSON file."""
    with open(HASH_STORE, "w") as f:
        json.dump(hashes, f, indent=4)

def check_files(file_list):
    stored_hashes = load_hashes()
    updated_hashes = {}

    print("\n=== Checking Files ===")
    for file_path in file_list:
        file_path = file_path.strip()
        current_hash = calculate_hash(file_path)

        if current_hash:
            previous_hash = stored_hashes.get(file_path)
            updated_hashes[file_path] = current_hash

            if previous_hash:
                if current_hash == previous_hash:
                    print(f"[OK] No change in: {file_path}")
                else:
                    print(f"[ALERT] File changed: {file_path}")
            else:
                print(f"[NEW] File added to tracking: {file_path}")

    save_hashes(updated_hashes)

def main():
    print("=== File Integrity Checker ===")
    files_input = input("Enter file names or full paths (comma-separated): ")
    file_list = files_input.split(",")
    file_list = [f.strip() for f in file_list if f.strip()]

    if file_list:
        check_files(file_list)
    else:
        print("No valid files provided.")

if _name_ == "_main_":
    main()