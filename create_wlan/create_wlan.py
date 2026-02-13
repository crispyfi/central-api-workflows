import json
import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pycentral import NewCentralBase
from pycentral.profiles import Profiles
from pycentral.scopes import Scopes
from pycentral.utils.url_utils import generate_url

def create_profile(
    endpoint,
    bulk_key,
    profile_name,
    config_file,
    central_conn,
    env,
    variables,
    device_persona,
    scope_type,
    scope_name
    ):
    """
    :param endpoint:
    :param bulk_key:
    :param profile_name:
    :param config_file:
    """

    # Load and render JSON template
    try:
        template = env.get_template(config_file)
        rendered_json = template.render(variables)
    except TemplateNotFound:
        print(f"Error: Config file '{config_file}' not found.")
        return 1
    except Exception as e:
        print(f"Error rendering template '{config_file}': {e}")
        return 1

    # Convert rendered JSON string to dict
    try:
        config_dict = json.loads(rendered_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing rendered JSON '{config_file}': {e}")
        return 1

    # Create API endpoint URL
    url = generate_url(api_endpoint=endpoint)

    # Create Profile
    print(f"\nCreating {endpoint} profile...\n")
    create_profile = Profiles.create_profile(
        bulk_key=bulk_key,
        path=url,
        central_conn=central_conn,
        config_dict=config_dict,
    )

    print(create_profile)

    # Assign Profile to Scope
    scopes = Scopes(central_conn)
    result = scopes.assign_profile_to_scope(
        profile_name = f"{endpoint}/{profile_name}",
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

def main():

    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader("."))

    # Load YAML variables
    variables_input = "vars.yaml"

    try:
        with open(variables_input, "r") as yaml_file:
            variables = yaml.safe_load(yaml_file)
    except FileNotFoundError:
        print(f"Error: YAML file '{variables_input}' not found.")
        return 1
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{variables_input}': {e}")
        return 1
        
    # Load profile assignment variables
    device_persona = variables["assignment"]["device_persona"]
    scope_type = variables["assignment"]["scope_type"]
    scope_name = variables["assignment"]["scope_name"]

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
    
    # Create and assign SSID Profile

    create_profile(
        "wlan-ssids",
        "wlan-ssid",
        variables["ssid"]["name"],
        "wlan-ssids.json",
        central_conn=central_conn,
        env=env,
        variables=variables,
        device_persona=device_persona,
        scope_type=scope_type,
        scope_name=scope_name
    )

    # Create and assign NTP Profile

    create_profile(
        "ntp",
        "profile",
        variables["ntp"]["name"],
        "ntp.json",
        central_conn=central_conn,
        env=env,
        variables=variables,
        device_persona=device_persona,
        scope_type=scope_type,
        scope_name=scope_name
    )

if __name__ == "__main__":
    exit(main())