import os
import re

def fix_tf_files():
    for root, dirs, files in os.walk('benchmarks'):
        for file in files:
            if file.endswith('.tf'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find all provider "aws" blocks that don't have skip_credentials_validation
                # This is a simple regex that matches `provider "aws" { ... }` blocks
                # and inserts the missing flags if not present.
                
                def replacer(match):
                    block = match.group(0)
                    if 'skip_credentials_validation' not in block:
                        # Insert flags after the first opening brace
                        flags = """
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
"""
                        return block.replace('{', '{' + flags, 1)
                    return block

                new_content = re.sub(r'provider\s+"aws"\s+\{([^}]*)\}', replacer, content)

                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed {path}")

if __name__ == '__main__':
    fix_tf_files()
