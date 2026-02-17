import json
import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pycentral import NewCentralBase
from pycentral.profiles import Profiles
from pycentral.scopes import Scopes
from pycentral.utils.url_utils import generate_url

def create_profile(
    *,
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
    :param endpoint: API endpoint for the profile type (e.g., "wlan-ssids", "ntp", etc).
    :param bulk_key: The key used for bulk profile creation in the API payload (e.g., "wlan-ssid", "profile", etc).
    :param profile_name: The name of the profile to be created, which will be read from the variables YAML file.
    :param config_file: The JSON template file for the profile configuration (e.g., "wlan-ssids.json", "ntp.json", etc).
    :param central_conn: An instance of the Central connection object created using NewCentralBase.
    :param env: The Jinja2 Environment object used to load and render the JSON template.
    :param variables: A dictionary of variables loaded from the YAML file, which will be used to render the JSON template.
    :param device_persona: The device persona to which the profile will be assigned, read from the variables YAML file.
    :param scope_type: The type of scope to which the profile will be assigned (e.g., "group", "site", etc.), read from the variables YAML file.
    :param scope_name: The name of the scope to which the profile will be assigned, read from the variables YAML file.
    """

    # Load and render JSON template
    try:
        template = env.get_template(config_file)
        rendered_json = template.render(variables)
    except TemplateNotFound:
        print(f"Error: Config file '{config_file}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error rendering template '{config_file}': {e}")
        exit(1)

    # Convert rendered JSON string to dict
    try:
        config_dict = json.loads(rendered_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing rendered JSON '{config_file}': {e}")
        exit(1)

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
    
    # Create and assign Radio Profile

    create_profile(
        endpoint="radios",
        bulk_key="profile",
        profile_name=variables["radio"]["name"],
        config_file="radios.json",
        central_conn=central_conn,
        env=env,
        variables=variables,
        device_persona=device_persona,
        scope_type=scope_type,
        scope_name=scope_name,
    )

    # Create and assign IDS Profile

    create_profile(
        endpoint="ids",
        bulk_key="profile",
        profile_name=variables["ids"]["name"],
        config_file="ids.json",
        central_conn=central_conn,
        env=env,
        variables=variables,
        device_persona=device_persona,
        scope_type=scope_type,
        scope_name=scope_name,
    )

    # Create and assign NTP Profile

    create_profile(
        endpoint="ntp",
        bulk_key="profile",
        profile_name=variables["ntp"]["name"],
        config_file="ntp.json",
        central_conn=central_conn,
        env=env,
        variables=variables,
        device_persona=device_persona,
        scope_type=scope_type,
        scope_name=scope_name,
    )

if __name__ == "__main__":
    exit(main())