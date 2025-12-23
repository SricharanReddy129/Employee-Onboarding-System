import re
import sys

def fix_relationships(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match relationship() calls without lazy parameter
    # This handles multiline relationships
    pattern = r"(relationship\([^)]+)(\))"
    
    def add_lazy(match):
        relationship_content = match.group(1)
        # Check if lazy is already present
        if 'lazy=' in relationship_content:
            return match.group(0)  # Return unchanged
        # Add lazy="selectin" before closing parenthesis
        return f'{relationship_content}, lazy="selectin"{match.group(2)}'
    
    # Apply the fix
    fixed_content = re.sub(pattern, add_lazy, content)
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed relationships in {file_path}")

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python fix_async_models.py models.py")
#         print(sys.argv[1])
#         sys.exit(1)
file_path = r"C:\Users\Mounika.Pothamsetty\Employee-Onboarding-System\MySQL for DB\models.py"
fix_relationships(file_path)