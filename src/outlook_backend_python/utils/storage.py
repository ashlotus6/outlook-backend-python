# File system operations for saving results
import os
import datetime

def save_completed(first_name, last_name, email_prefix, password):
    """Save completed account information"""
    line = f"{first_name} {last_name} {email_prefix}@outlook.com {password}\n"
    file_path = os.path.join(os.getcwd(), 'completed.txt')
    
    # Create file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Outlook Account Creation Results\n")
            f.write(f"# Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Format: FirstName LastName Email Password\n\n")
    
    # Append the new account
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(line)
    
    print(f"Saved to {file_path}:\n{line.strip()}")

__all__ = ['save_completed']
