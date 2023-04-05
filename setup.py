import subprocess

print('Starting setup.')

files = ['create_tables.py', 'create_products.py', 'create_order.py']

for file in files:
    subprocess.run(['python', file])
    
print('Setup completed.')