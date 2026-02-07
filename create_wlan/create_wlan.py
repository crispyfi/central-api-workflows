import json

from pycentral import NewCentralBase
from pycentral.profiles import Profiles
from pycentral.scopes import Scopes
from pycentral.utils.url_utils import generate_url

# Define the profile assignment variables
device_persona = "CAMPUS_AP"
scope_type = "site_collection"
scope_name = "Lab"

def main():

    # Load the credentials from the JSON file
    credentials_file = "central_token.json"

    try:
        with open(credentials_file, "r") as file:
            credentials = json.load(file)
    except FileNotFoundError:
        print(f"Error: Credentials file {credentials_file} not found.")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file '{credentials_file}': {e}")
        return 1

    # Create connection to Central
    try:
        print("Connecting to Central...")
        central_conn = NewCentralBase(
            token_info=credentials, enable_scope=True, log_level="ERROR"
        )
        print("Connected to Central successfully!")
    except Exception as e:
        print(f"\nFailed to connect to Central: {e}")
        return 1

    # Load configuration file
    config_file = "wlan-ssid.json"

    try:
        with open(config_file, "r") as file:
            config_dict = json.load(file)
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found.")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file '{config_file}' {e}")
        return 1

    # Create API endpoint URL
    endpoint = "wlan-ssids"
    url = generate_url(api_endpoint=endpoint)

    bulk_key = "wlan-ssid"
    
    # Create Profile
    print(f"\nCreating {endpoint} profile...\n")
    create_profile = Profiles.create_profile(
        bulk_key=bulk_key,
        path=url,
        central_conn=central_conn,
        config_dict=config_dict,
    )

    print(create_profile)

    # Use the Scopes SDK to assign the SSID to the site
    scopes = Scopes(central_conn)
    result = scopes.assign_profile_to_scope(
        profile_name = f"{endpoint}/{config_dict['ssid']}",
        profile_persona=device_persona,
        scope=scope_type,
        scope_name=scope_name,
    )

    # Check the result and print appropriate messages
    if result:
        print(f"\nSuccessfully assigned profile to {scope_name}\n")
    else:
        print(f"\nError in assigning profile\n")
        exit()

if __name__ == "__main__":
    exit(main())