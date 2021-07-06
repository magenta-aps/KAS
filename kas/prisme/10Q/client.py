import pysftp
import tempfile

from getpass import getpass

# TODO: Rewrite this to be proper client module, this is just the basics

hostname = 'localhost'
port = 2222

hostkey = 'ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjEAAAAIbmlzdHA1MjEAAACFBACoOVgH2Cl8R9WPCsGP9rpZuF4H7aZ0S1kocGeqyVz5f1Ri3aJkxATeCB5xr4AUVZbaNW43L+cdIDZJZMSbJXGvtgFTSZYxsG3pKAzNQjQFVTcsfOHEJnbe0riGK5FBnFrll07MMO8jmU2hq5umLPZMpxjEQibHq99LDkyjIZmk/rRKhA=='

password = getpass("Enter password: ")

with tempfile.NamedTemporaryFile() as known_hosts_file:

    known_hosts_file.write((hostname + ' ' + hostkey + '\n').encode())
    known_hosts_file.flush()
    connection_options = pysftp.CnOpts(knownhosts=known_hosts_file.name)

    conn = pysftp.Connection(
        hostname,
        port=port,
        username='ftp_kas_nanoq@erp.gl',
        password=password,
        cnopts=connection_options
    )

    print(conn.listdir())

    # Close connection otherwise we get an Exception during teardown
    conn = None
