#!/usr/bin/python3
import os
from smb.SMBConnection import SMBConnection
from datetime import datetime


# Define common connection parameters
userID = 'asiair'
password = '12345678'
client_machine_name = 'localhost'
domain_name = 'WORKGROUP'

# Define the list of servers and their respective local folders
server_info = [
#    {'ip': '192.168.10.80', 'local_folder': 'asiair1'},
#    {'ip': '192.168.10.81', 'local_folder': 'asiair2'},
#    {'ip': '192.168.10.82', 'local_folder': 'asiair3'},
    {'ip': '192.168.10.83', 'local_folder': 'asiair4'},
    {'ip': '192.168.10.84', 'local_folder': 'asiair5'},
#    {'ip': '192.168.10.85', 'local_folder': 'asiair6'},
    # Add more servers and their local folders here
]

# Create a directory with today's date in the format DDMMYY
today_date = datetime.now().strftime("%d%m%y")

try:
    for server in server_info:
        conn = SMBConnection(userID, password, client_machine_name, server['ip'], domain=domain_name, use_ntlm_v2=True,
                             is_direct_tcp=True)
        conn.connect(server['ip'], 445)

        shares = conn.listShares()

        for share in shares:
            try:
                if not share.isSpecial and share.name != 'print$':
                    # Define the local destination directory based on the server's local folder and share name
                    local_destination_base = f'/mnt/j/new/asiair/{server["local_folder"]}/'
                    local_destination_dir = os.path.join(local_destination_base, today_date)
                    share_destination_dir = os.path.join(local_destination_dir, share.name)

                    # Create the corresponding local directory for today's date and the share name
                    os.makedirs(share_destination_dir, exist_ok=True)
                    print(f"Created local directory: {share_destination_dir}")

                    # Define a function to copy files and directories
                    def copy_files_and_dirs(remote_dir, local_dir):
                        sharedfiles = conn.listPath(share.name, remote_dir)
                        for sharedfile in sharedfiles:
                            if not sharedfile.filename in ['.', '..']:
                                remote_path = os.path.join(remote_dir, sharedfile.filename)
                                local_path = os.path.join(local_dir, sharedfile.filename)

                                if sharedfile.isDirectory:
                                    # Create the corresponding local directory
                                    os.makedirs(local_path, exist_ok=True)
                                    print(f"Created local directory: {local_path}")
                                    # Recursively copy files and subdirectories
                                    copy_files_and_dirs(remote_path, local_path)
                                else:
                                    # Check if the local file exists and has the same size
                                    if not os.path.exists(local_path) or os.path.getsize(local_path) != sharedfile.file_size:
                                        # Copy the file
                                        start_time = datetime.now()
                                        with open(local_path, 'wb') as local_file:
                                            conn.retrieveFile(share.name, remote_path, local_file)
                                        end_time = datetime.now()
                                        elapsed_time = (end_time - start_time).total_seconds()
                                        file_size_mb = sharedfile.file_size / (1024 * 1024)
                                        transfer_speed = file_size_mb / elapsed_time
                                        print(f"Copied file: {remote_path} to {local_path} ({file_size_mb:.2f} MB in {elapsed_time:.2f} seconds, {transfer_speed:.2f} MB/s)")
                                    else:
                                        print(f"Skipped file: {remote_path} (already exists with the same size)")

                    # Copy files and directories to the local destination directory
                    copy_files_and_dirs('/', share_destination_dir)

                    print(f"Successfully copied files from {share.name} on server {server['ip']} to {share_destination_dir}")

            except Exception as e:
                print(f"Error copying files from {share.name} on server {server['ip']}: {str(e)}")

        conn.close()

    # Delete empty directories in the local destination
    for server in server_info:
        local_destination_base = f'/mnt/j/new/asiair/{server["local_folder"]}/'
        local_destination_dir = os.path.join(local_destination_base, today_date)
        for root, dirs, files in os.walk(local_destination_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"Deleted empty directory: {dir_path}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
