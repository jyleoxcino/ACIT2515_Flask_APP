import subprocess

print('Starting setup.')

files = ['create_tables.py', 'create_products.py']

for file in files:
    subprocess.run(['python', file])
    
print('Setup completed.')