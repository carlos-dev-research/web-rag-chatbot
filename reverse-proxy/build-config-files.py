import os
import subprocess

def generate_nginx_config(ip_address, template_file, output_dir):
    """Generates the Nginx configuration using a template file."""
    # Read the Nginx template file
    with open(template_file, 'r') as f:
        nginx_template = f.read()

    # Replace the placeholder with the actual IP address
    nginx_config = nginx_template.format(ip_address=ip_address)

    # Write the new Nginx config file
    output_file = os.path.join(output_dir, 'nginx.conf')
    with open(output_file, 'w') as f:
        f.write(nginx_config)
    
    print(f"Nginx configuration written to {output_file}")


def generate_ssl_cert(ip_address, cert_dir):
    """Generates a self-signed SSL certificate for the provided IP address."""
    cert_file = os.path.join(cert_dir, 'cert.pem')
    key_file = os.path.join(cert_dir, 'key.pem')

    # Create the directory if it doesn't exist
    os.makedirs(cert_dir, exist_ok=True)

    # Generate the self-signed certificate using OpenSSL
    try:
        subprocess.run([
            'openssl', 'req', '-x509', '-nodes', '-days', '365',
            '-newkey', 'rsa:2048',
            '-keyout', key_file,
            '-out', cert_file,
            '-subj', f'/CN={ip_address}'
        ], check=True)
        print(f"Self-signed SSL certificate and key generated in {cert_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating SSL certificate: {e}")
        exit(1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate Nginx configuration and self-signed SSL certificate for a specified IP address.")
    parser.add_argument('ip_address', help="The IP address to configure.")
    parser.add_argument('--template-file', default='nginx_template.conf', help="Path to the Nginx template file (default: nginx_template.conf).")
    parser.add_argument('--output-dir', default='.', help="The output directory for generated files (default is current directory).")
    parser.add_argument('--cert-dir', default='./certs', help="The directory where SSL certificates will be stored (default: ./certs).")

    args = parser.parse_args()

    output_dir = args.output_dir
    cert_dir = args.cert_dir

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate Nginx configuration
    generate_nginx_config(args.ip_address, args.template_file, output_dir)

    # Generate SSL certificates
    generate_ssl_cert(args.ip_address, cert_dir)

if __name__ == "__main__":
    main()
